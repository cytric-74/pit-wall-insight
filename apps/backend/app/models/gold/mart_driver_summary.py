"""`mart_driver_summary` — one row per driver per season (docs/07_DATABASE_SCHEMA.md).

docs' column list has no season scope for this table, but "wins",
"podiums", etc. are meaningless without one, and this pipeline only ever
transforms one season at a time (`run_transform(season=...)`) — so
`season_id` is added here as a documented extension. `driver` denormalizes
`dim_driver.full_name` directly onto the row, matching docs' literal
column name and letting a consumer read this mart without an extra join
for the common case of just wanting a name to display.

`consistency_score`/`pit_efficiency`/`race_pace`/`qualifying_pace` are
real computations from `fct_results`/`fct_laps`/`fct_pitstop` — see
`apps/ingestion/transformers/bronze_to_gold.py` for the exact formulas,
each documented at its point of computation since docs/07 doesn't define
them itself.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import GoldBase
from app.models.mixins import GoldAuditMixin


class MartDriverSummary(GoldBase, GoldAuditMixin):
    __tablename__ = "mart_driver_summary"
    __table_args__ = (
        UniqueConstraint("season_id", "driver_id", name="uq_mart_driver_summary_natural_key"),
    )

    mart_driver_summary_id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    season_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("dim_season.season_id"), nullable=False, index=True
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("dim_driver.driver_id"), nullable=False, index=True
    )
    driver: Mapped[str] = mapped_column(nullable=False)
    wins: Mapped[int] = mapped_column(nullable=False)
    podiums: Mapped[int] = mapped_column(nullable=False)
    poles: Mapped[int] = mapped_column(nullable=False)
    fastest_laps: Mapped[int] = mapped_column(nullable=False)
    average_finish: Mapped[float | None] = mapped_column(nullable=True)
    average_qualifying: Mapped[float | None] = mapped_column(nullable=True)
    consistency_score: Mapped[float | None] = mapped_column(nullable=True)
    pit_efficiency: Mapped[float | None] = mapped_column(nullable=True)
    race_pace: Mapped[float | None] = mapped_column(nullable=True)
    qualifying_pace: Mapped[float | None] = mapped_column(nullable=True)
