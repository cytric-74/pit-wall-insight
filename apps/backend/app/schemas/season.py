"""Response DTOs for `/seasons*` (docs/08_API_SPECIFICATION.md — "Seasons").

Standings entries (`DriverStandingEntry`/`ConstructorStandingEntry`) are
shared with `app/schemas/dashboard.py`, since `/dashboard` and
`/seasons/{year}/standings` present the same ranked-by-points shape for
different scopes (latest season vs. a chosen one).
"""

from __future__ import annotations

from app.schemas.base import CamelModel


class DriverStandingEntry(CamelModel):
    position: int
    driver: str
    team: str | None
    points: float
    wins: int


class ConstructorStandingEntry(CamelModel):
    position: int
    constructor: str
    points: float
    wins: int


class StandingsData(CamelModel):
    season: int
    drivers: list[DriverStandingEntry]
    constructors: list[ConstructorStandingEntry]


class SeasonListItem(CamelModel):
    year: int
    race_count: int
    sprint_count: int | None
    champion_driver: str | None
    champion_constructor: str | None


class SeasonSummary(CamelModel):
    year: int
    race_count: int
    sprint_count: int | None
    champion_driver: str | None
    champion_constructor: str | None
    fastest_lap_driver: str | None
    fastest_lap_time: float | None
    fastest_pitstop: float | None
    average_overtakes: float | None
    championship_gap: float | None


class CalendarEntry(CamelModel):
    round: int
    race_name: str | None
    date: str | None
    circuit: str | None
    country: str | None
