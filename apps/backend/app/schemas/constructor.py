"""Response DTOs for `/constructors*` (docs/08_API_SPECIFICATION.md — "Constructors")."""

from __future__ import annotations

import uuid

from app.schemas.base import CamelModel


class Constructor(CamelModel):
    id: uuid.UUID
    team_name: str
    base_country: str | None
    active: bool | None


class ConstructorSeasonSummary(CamelModel):
    season: int
    wins: int
    podiums: int
    pitstop_average: float | None
    strategy_success: float | None
    average_points: float | None
    dnf_rate: float | None
    development_index: float | None
    average_pace: float | None


class ConstructorCareerStatistics(CamelModel):
    constructor: str
    seasons_competed: int
    wins: int
    podiums: int
    average_points: float | None
    dnf_rate: float | None
