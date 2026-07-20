"""Response DTOs for `/sessions*` (docs/08_API_SPECIFICATION.md — "Sessions")."""

from __future__ import annotations

import uuid

from app.schemas.base import CamelModel


class SessionMetadata(CamelModel):
    id: uuid.UUID
    season: int
    round: int
    race_name: str | None
    session_type: str
    circuit: str | None
    date: str | None


class SessionResultEntry(CamelModel):
    driver: str
    team: str | None
    grid_position: float | None
    finish_position: float | None
    points: float | None
    status: str | None
    fastest_lap: bool | None
    laps_completed: int | None


class SessionLapEntry(CamelModel):
    driver: str
    lap_number: float
    lap_time: float | None
    compound: str | None
    tyre_life: float | None
    position: float | None
    pit_in: bool | None
    pit_out: bool | None
