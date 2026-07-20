"""`mart_race_summary` — one row per race session (docs/07_DATABASE_SCHEMA.md).

Grain: one row per `session_id` where `session_type="R"` — a race, not
every practice/qualifying session — `session_id` doubles as this table's
primary key and foreign key into `dim_session` for the same 1:1 reason
`mart_dashboard.season_id` does (see that model's docstring).

`safety_car_laps`/`red_flags` have no source in this pipeline (no race
control message data is collected) and are left `NULL`. `weather` is a
short descriptive label ("Dry"/"Wet"/`None`) derived from
`dim_weather.rainfall` for the session, not a foreign key — a mart is
meant to be display-ready, and a consumer wanting the full weather detail
already has `dim_session.weather_id` -> `dim_weather` for that.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import GoldBase
from app.models.mixins import GoldAuditMixin


class MartRaceSummary(GoldBase, GoldAuditMixin):
    __tablename__ = "mart_race_summary"

    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("dim_session.session_id"), primary_key=True
    )
    race: Mapped[str | None] = mapped_column(nullable=True)
    winner: Mapped[str | None] = mapped_column(nullable=True)
    pole: Mapped[str | None] = mapped_column(nullable=True)
    fastest_lap: Mapped[str | None] = mapped_column(nullable=True)
    average_pitstop: Mapped[float | None] = mapped_column(nullable=True)
    safety_car_laps: Mapped[int | None] = mapped_column(nullable=True)
    red_flags: Mapped[int | None] = mapped_column(nullable=True)
    weather: Mapped[str | None] = mapped_column(nullable=True)
    retirements: Mapped[int | None] = mapped_column(nullable=True)
