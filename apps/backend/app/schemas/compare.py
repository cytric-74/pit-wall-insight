"""Response DTOs for `/compare/*` (docs/08_API_SPECIFICATION.md — "Comparison").

`/compare/drivers` reuses `app/schemas/driver.py`'s `DriverComparison` (the
same shape `/drivers/{id}/comparison/{otherId}` already returns — docs/08
lists both routes, but there's only one sensible comparison result for a
pair of drivers).
"""

from __future__ import annotations

from app.schemas.base import CamelModel
from app.schemas.race import RaceSummary


class ConstructorComparisonEntry(CamelModel):
    constructor: str
    wins: int
    podiums: int
    pitstop_average: float | None
    strategy_success: float | None
    average_points: float | None
    dnf_rate: float | None
    development_index: float | None
    average_pace: float | None


class ConstructorComparison(CamelModel):
    season: int
    constructor_a: ConstructorComparisonEntry
    constructor_b: ConstructorComparisonEntry


class RaceComparison(CamelModel):
    race_a: RaceSummary
    race_b: RaceSummary
