"""Per-record validation runner.

Purpose
-------
Takes the raw, unvalidated output of a collector function and a Pydantic
model describing the expected shape (from `validators/schema.py`), and
validates each record independently. This is the one place in the pipeline
that implements docs/06_DATA_ENGINEERING.md's validator contract literally:
"Validation failures are logged. Pipeline should continue where possible" —
a single malformed record is set aside and logged with enough context to
debug it, while every other record in the batch is still processed.

Inputs
------
- `model`: a Pydantic model class from `validators/schema.py`.
- `raw_records`: the `list[dict[str, Any]]` a collector function returned.
- `source`: which upstream produced this batch (e.g. `"fastf1"`,
  `"jolpica"`) — included in every log line so a failure can be traced back
  to the API that sent the bad data.
- `entity`: what kind of record this is (e.g. `"session_result"`) — same
  reasoning as `source`.
- `natural_key_field`: optional field name (e.g. `"DriverNumber"`,
  `"driverId"`) to pull out and include in log/issue output even when
  validation fails on a *different* field — without this, a record that
  fails validation on, say, `LapTime` would otherwise be nearly impossible
  to identify in a batch of hundreds.

Outputs
-------
A `ValidationResult`: the list of successfully-validated model instances,
and the list of `ValidationIssue`s describing every record that was
rejected and why.

Time complexity
----------------
O(n) in the number of raw records — each record is validated exactly once,
independent of every other record in the batch.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError
from pydantic_core import ErrorDetails

logger = logging.getLogger("ingestion.validators")

# PEP 695's `def f[T](...)` syntax would be preferred (and is what
# `target-version = "py312"` in pyproject.toml otherwise implies), but it
# requires the interpreter *running* mypy/ruff to itself be 3.12+ to parse —
# this project's available toolchain is 3.11. A `TypeVar` is portable across
# interpreter versions and behaves identically at both type-check and
# runtime, so it's used here instead.
ModelT = TypeVar("ModelT", bound=BaseModel)


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """One rejected record, with enough context to find and fix it.

    `index` is the record's position in the *original* batch (not the
    position among other failures), so it can be cross-referenced against
    the raw collector output directly. `errors` is Pydantic's own
    structured error list (`ValidationError.errors()`) — field path, error
    type, and message — rather than a flattened string, so a caller that
    wants to (for example) count how many failures were "missing field" vs
    "wrong type" can do so without re-parsing a message.
    """

    index: int
    natural_key: Any | None
    errors: list[ErrorDetails]


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """The outcome of validating one batch of raw records against one model."""

    valid: list[BaseModel]
    issues: list[ValidationIssue]

    @property
    def valid_count(self) -> int:
        return len(self.valid)

    @property
    def issue_count(self) -> int:
        return len(self.issues)


def validate_records(
    model: type[ModelT],
    raw_records: list[dict[str, Any]],
    *,
    source: str,
    entity: str,
    natural_key_field: str | None = None,
) -> ValidationResult:
    """Validate every record in `raw_records` against `model`, independently.

    See module docstring for the full contract. The critical invariant:
    this function never raises because of a single record's content — the
    only way it can raise is if `raw_records` itself isn't iterable, which
    would indicate a collector bug, not a data problem.
    """
    # Typed as `list[BaseModel]` rather than `list[ModelT]`: `list` is
    # invariant, so a `list[ModelT]` can't be passed where
    # `ValidationResult.valid: list[BaseModel]` is expected even though
    # `ModelT` is bound to `BaseModel` — callers that need the narrower
    # type back can still get it via `model.model_validate` themselves, or
    # by construction (every element here genuinely is a `model` instance).
    valid: list[BaseModel] = []
    issues: list[ValidationIssue] = []

    for index, record in enumerate(raw_records):
        try:
            parsed = model.model_validate(record)
        except ValidationError as exc:
            natural_key = record.get(natural_key_field) if natural_key_field else None
            issue = ValidationIssue(index=index, natural_key=natural_key, errors=exc.errors())
            issues.append(issue)
            logger.warning(
                "Validation failed for %s record #%d (source=%s, natural_key=%s): %s",
                entity,
                index,
                source,
                natural_key,
                issue.errors,
            )
            continue
        valid.append(parsed)

    return ValidationResult(valid=valid, issues=issues)
