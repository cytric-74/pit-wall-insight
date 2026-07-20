"""Response DTOs for `/circuits*` (docs/08_API_SPECIFICATION.md — "Circuits")."""

from __future__ import annotations

import uuid

from app.schemas.base import CamelModel


class Circuit(CamelModel):
    id: uuid.UUID
    name: str
    country: str | None
    city: str | None
    latitude: float | None
    longitude: float | None


class CircuitRaceHistoryEntry(CamelModel):
    season: int
    round: int
    race_name: str | None
    winner: str | None
    pole: str | None
    fastest_lap: str | None


class CircuitRecord(CamelModel):
    driver: str | None
    lap_time: float | None
    season: int | None
    round: int | None
