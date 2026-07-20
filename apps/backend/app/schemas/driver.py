"""Response DTOs for `/drivers*` (docs/08_API_SPECIFICATION.md — "Drivers").

`Driver` is used for both the list and the single-profile endpoint — docs/08
doesn't describe the profile as carrying more fields than the list entry,
so one schema covers both rather than inventing a distinction that isn't
specified anywhere.
"""

from __future__ import annotations

import uuid
from datetime import date

from app.schemas.base import CamelModel


class Driver(CamelModel):
    id: uuid.UUID
    driver_number: int | None
    full_name: str
    abbreviation: str | None
    nationality: str | None
    date_of_birth: date | None
    team_id: uuid.UUID | None
    team: str | None
    rookie_season: int | None
    world_titles: int | None
    active: bool | None


class SeasonDriverSummary(CamelModel):
    season: int
    wins: int
    podiums: int
    poles: int
    fastest_laps: int
    average_finish: float | None
    average_qualifying: float | None
    consistency_score: float | None
    pit_efficiency: float | None
    race_pace: float | None
    qualifying_pace: float | None


class DriverCareerStatistics(CamelModel):
    driver: str
    seasons_competed: int
    wins: int
    podiums: int
    poles: int
    fastest_laps: int
    average_finish: float | None
    consistency_score: float | None


class DriverLap(CamelModel):
    season: int
    round: int
    race_name: str | None
    session_type: str
    lap_number: float
    lap_time: float | None
    sector_1: float | None
    sector_2: float | None
    sector_3: float | None
    compound: str | None
    tyre_life: float | None
    position: float | None
    pit_in: bool | None
    pit_out: bool | None


class SeasonConsistencyEntry(CamelModel):
    season: int
    consistency_score: float | None
    average_finish: float | None


class DriverConsistency(CamelModel):
    driver: str
    career_consistency_score: float | None
    seasons: list[SeasonConsistencyEntry]


class DriverComparisonEntry(CamelModel):
    driver: str
    wins: int
    podiums: int
    poles: int
    fastest_laps: int
    average_finish: float | None
    average_qualifying: float | None
    consistency_score: float | None
    pit_efficiency: float | None
    race_pace: float | None
    qualifying_pace: float | None


class DriverComparison(CamelModel):
    season: int
    driver_a: DriverComparisonEntry
    driver_b: DriverComparisonEntry
