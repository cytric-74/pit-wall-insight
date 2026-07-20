"""Shared helpers reused across `app/services/*.py`.

Six services each reimplemented the identical "fetch (or check), raise
`NotFoundError` if missing" shape byte-for-byte, and `driver_service.py`/
`constructor_service.py` each defined a byte-identical `mean()` helper —
no shared utility abstracted either pattern despite the repetition
(Phase 7 audit, Medium). This is the one copy every service now calls.

Also the one place a `NotFoundError` is logged before being raised — until
now, no repository or service logged anything at all; a 404 raised deep in
a service left no diagnostic breadcrumb beyond the final HTTP response
(Phase 7 audit, Medium).
"""

from __future__ import annotations

import logging
import statistics
from collections.abc import Awaitable, Mapping
from typing import TypeVar

from app.exceptions.base import NotFoundError

logger = logging.getLogger("app.services")

# PEP 695 `def get_or_404[T](...)` syntax is Python 3.12+ only; this
# project's actual interpreter (see apps/backend/.venv) is 3.11 despite
# pyproject.toml's `target-version`/`python_version` both saying 3.12, so
# the classic `TypeVar` form is what actually runs.
T = TypeVar("T")


async def get_or_404(fetch: Awaitable[T | None], message: str) -> T:  # noqa: UP047
    """Await `fetch`; raise `NotFoundError(message)` if it resolves to `None`."""
    result = await fetch
    if result is None:
        logger.debug("not found: %s", message)
        raise NotFoundError(message)
    return result


async def ensure_or_404(fetch: Awaitable[bool], message: str) -> None:
    """Await `fetch`; raise `NotFoundError(message)` if it resolves falsy."""
    if not await fetch:
        logger.debug("not found: %s", message)
        raise NotFoundError(message)


def mean(values: list[float | None]) -> float | None:
    """Average of the non-`None` values in `values`; `None` if none are present."""
    present = [value for value in values if value is not None]
    return statistics.fmean(present) if present else None


def resolve_comparison_season(
    summaries_a: Mapping[int, object],
    summaries_b: Mapping[int, object],
    season: int | None,
    *,
    entity_a_name: str,
    entity_b_name: str,
) -> int:
    """Resolve which season a two-entity comparison should use.

    An explicit `season` is used as-is (still validated below). Otherwise
    the latest season both entities have a summary row for is picked —
    `compare_drivers` and `compare_constructors` each reimplemented this
    identical ~30-line block, differing only in the entity-name strings
    used in the resulting error message (Phase 7 audit, Medium).
    """
    if season is not None:
        resolved_season = season
    else:
        common_seasons = set(summaries_a) & set(summaries_b)
        if not common_seasons:
            raise NotFoundError(
                f"No season with data for both {entity_a_name} and {entity_b_name}."
            )
        resolved_season = max(common_seasons)

    if resolved_season not in summaries_a or resolved_season not in summaries_b:
        raise NotFoundError(
            f"Season {resolved_season} has no data for both "
            f"{entity_a_name} and {entity_b_name}."
        )
    return resolved_season
