"""Response DTOs for `/dashboard` and `/dashboard/highlights` (docs/08_API_SPECIFICATION.md).

`DashboardData` intentionally exposes `fastest_pitstop` rather than an
"average pit stop" field: docs/08's prose lists "Average pit stop" as a
dashboard KPI, but docs/07_DATABASE_SCHEMA.md's `mart_dashboard` column set
(the actual Phase 4 deliverable) only has `fastest_pitstop` — there is no
average computed anywhere in the warehouse. Following the schema that was
actually built rather than the prose it's paraphrased from.
"""

from __future__ import annotations

from app.schemas.base import CamelModel
from app.schemas.season import ConstructorStandingEntry, DriverStandingEntry


class RecentRace(CamelModel):
    round: int
    race_name: str | None
    winner: str | None
    date: str | None


class DashboardData(CamelModel):
    season: int
    champion_driver: str | None
    champion_constructor: str | None
    driver_standings: list[DriverStandingEntry]
    constructor_standings: list[ConstructorStandingEntry]
    recent_races: list[RecentRace]
    fastest_lap_driver: str | None
    fastest_lap_time: float | None
    fastest_pitstop: float | None
    average_overtakes: float | None
    championship_gap: float | None


class DashboardHighlights(CamelModel):
    race_name: str | None
    winner: str | None
    pole: str | None
    fastest_lap: str | None
    retirements: int | None
    weather: str | None
