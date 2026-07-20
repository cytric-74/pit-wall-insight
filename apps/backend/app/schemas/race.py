"""Response DTOs for `/races*` (docs/08_API_SPECIFICATION.md — "Races").

"Race" identifiers are `dim_session.session_id` UUIDs, scoped to
`session_type == "R"` rows — races aren't a separate Gold entity, they're
race sessions (see `app/models/gold/session.py`).

`RaceWeather` is a single per-session snapshot, not a time series: docs/08
calls this "Weather evolution", but `dim_weather` is deliberately one
aggregated row per session (see `app/models/gold/weather.py`) — there is no
FastF1-sample-level time series retained past the Gold transform.
`RaceStrategyEntry` is derived from tyre-compound *changes* across
`fct_laps` (not `fct_pitstop`), since Phase 4's pit-stop detection only
catches stops recorded on a single lap row (see `app/models/gold/pitstop.py`)
and would otherwise leave this endpoint mostly empty.
"""

from __future__ import annotations

import uuid

from app.schemas.base import CamelModel


class RaceListItem(CamelModel):
    id: uuid.UUID
    season: int
    round: int
    race_name: str | None
    circuit: str | None
    country: str | None
    date: str | None
    winner: str | None


class RaceSummary(CamelModel):
    id: uuid.UUID
    season: int
    round: int
    race_name: str | None
    circuit: str | None
    country: str | None
    date: str | None
    winner: str | None
    pole: str | None
    fastest_lap: str | None
    retirements: int | None
    weather: str | None
    average_pitstop: float | None


class PositionEntry(CamelModel):
    driver: str
    lap_number: float
    position: float | None


class PitstopEntry(CamelModel):
    driver: str
    lap: float
    pit_duration: float | None
    stop_number: int | None
    compound_before: str | None
    compound_after: str | None


class RaceWeather(CamelModel):
    air_temperature: float | None
    track_temperature: float | None
    humidity: float | None
    wind_speed: float | None
    wind_direction: float | None
    rainfall: bool | None
    pressure: float | None


class TyreStint(CamelModel):
    compound: str | None
    start_lap: float
    end_lap: float
    lap_count: int


class DriverStrategy(CamelModel):
    driver: str
    stints: list[TyreStint]
