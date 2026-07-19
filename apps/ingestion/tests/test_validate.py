"""Unit tests for `validators.validate.validate_records`.

What's being verified: the central contract this module exists to
implement — a batch of raw records validates independently, record by
record, with a failure on one record never affecting any other record in
the same batch, and never raising out of `validate_records` itself.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from validators.validate import validate_records


class _Sample(BaseModel):
    """A minimal model standing in for a real `validators/schema.py` model —
    intentionally simple so these tests exercise `validate_records`'
    partitioning logic, not any particular real schema's field rules."""

    id: str
    value: int


def test_all_valid_records_are_returned_and_no_issues_are_raised() -> None:
    records = [{"id": "a", "value": 1}, {"id": "b", "value": 2}]
    result = validate_records(_Sample, records, source="test", entity="sample")

    assert result.valid_count == 2
    assert result.issue_count == 0
    assert [record.id for record in result.valid] == ["a", "b"]  # type: ignore[attr-defined]


def test_an_invalid_record_is_rejected_without_raising() -> None:
    records = [{"id": "a", "value": "not-an-int"}]
    result = validate_records(_Sample, records, source="test", entity="sample")

    assert result.valid_count == 0
    assert result.issue_count == 1
    assert result.issues[0].index == 0


def test_a_mixed_batch_partitions_correctly() -> None:
    """The critical property: one bad record must not affect its neighbors —
    the batch continues past it (docs/06_DATA_ENGINEERING.md: 'Validation
    failures are logged. Pipeline should continue where possible.')."""
    records: list[dict[str, Any]] = [
        {"id": "a", "value": 1},
        {"id": "b", "value": "bad"},
        {"id": "c", "value": 3},
    ]
    result = validate_records(_Sample, records, source="test", entity="sample")

    assert result.valid_count == 2
    assert result.issue_count == 1
    assert [record.id for record in result.valid] == ["a", "c"]  # type: ignore[attr-defined]
    assert result.issues[0].index == 1


def test_natural_key_is_captured_from_the_failing_record() -> None:
    records = [{"id": "known-id", "value": "bad"}]
    result = validate_records(
        _Sample, records, source="test", entity="sample", natural_key_field="id"
    )

    assert result.issues[0].natural_key == "known-id"


def test_missing_natural_key_field_defaults_to_none() -> None:
    records = [{"id": "a", "value": "bad"}]
    result = validate_records(_Sample, records, source="test", entity="sample")

    assert result.issues[0].natural_key is None


def test_missing_required_field_is_a_validation_issue_not_an_exception() -> None:
    records = [{"value": 1}]  # missing required "id"
    result = validate_records(_Sample, records, source="test", entity="sample")

    assert result.issue_count == 1
    assert result.valid_count == 0


def test_an_empty_batch_returns_an_empty_result() -> None:
    result = validate_records(_Sample, [], source="test", entity="sample")

    assert result.valid_count == 0
    assert result.issue_count == 0
