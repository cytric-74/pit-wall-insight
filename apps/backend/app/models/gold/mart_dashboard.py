"""`mart_dashboard` — one row per season, the season-at-a-glance KPI set (docs/07_DATABASE_SCHEMA.md).

Grain: one row per season — `season_id` doubles as this table's primary
key and its foreign key into `dim_season`, since the two are always in
1:1 correspondence (no separate surrogate id is needed for a table that
can never have more than one row per season).

`fastest_lap_time`/`fastest_lap_driver` split docs' single `fastest_lap`
column in two: a mart is meant to be display-ready, and a bare lap time
without whose lap it was is not independently useful on a dashboard card.

`average_overtakes`, `fastest_pitstop`, and `championship_gap` are real
computations (see `apps/ingestion/transformers/bronze_to_gold.py`), not
placeholders — `average_overtakes` specifically is a documented
approximation (consecutive-lap position improvements, halved, since one
overtake changes two drivers' positions), not an exact count from race
control data this pipeline doesn't have.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import GoldBase
from app.models.mixins import GoldAuditMixin


class MartDashboard(GoldBase, GoldAuditMixin):
    __tablename__ = "mart_dashboard"

    season_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("dim_season.season_id"), primary_key=True
    )
    season: Mapped[int] = mapped_column(nullable=False)
    drivers: Mapped[int] = mapped_column(nullable=False)
    constructors: Mapped[int] = mapped_column(nullable=False)
    races: Mapped[int] = mapped_column(nullable=False)
    fastest_pitstop: Mapped[float | None] = mapped_column(nullable=True)
    average_overtakes: Mapped[float | None] = mapped_column(nullable=True)
    fastest_lap_time: Mapped[float | None] = mapped_column(nullable=True)
    fastest_lap_driver: Mapped[str | None] = mapped_column(nullable=True)
    championship_gap: Mapped[float | None] = mapped_column(nullable=True)
