"""`mart_constructor_summary` — one row per constructor per season (docs/07_DATABASE_SCHEMA.md).

Same season-scoping rationale as `mart_driver_summary` — see that model's
docstring. `strategy_success` and `development_index` have no source in
this pipeline (the former needs undercut/overcut modeling, explicitly
deferred alongside Strategy Lab; the latter would need a multi-season pace
trend this project doesn't compute) and are left `NULL` rather than
fabricated, consistent with every other "no source yet" field across the
Gold layer (e.g. `dim_circuit.length`, `dim_constructor.power_unit`).
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import GoldBase
from app.models.mixins import GoldAuditMixin


class MartConstructorSummary(GoldBase, GoldAuditMixin):
    __tablename__ = "mart_constructor_summary"
    __table_args__ = (
        UniqueConstraint(
            "season_id", "constructor_id", name="uq_mart_constructor_summary_natural_key"
        ),
    )

    mart_constructor_summary_id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    season_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("dim_season.season_id"), nullable=False, index=True
    )
    constructor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("dim_constructor.constructor_id"), nullable=False, index=True
    )
    constructor: Mapped[str] = mapped_column(nullable=False)
    wins: Mapped[int] = mapped_column(nullable=False)
    podiums: Mapped[int] = mapped_column(nullable=False)
    pitstop_average: Mapped[float | None] = mapped_column(nullable=True)
    strategy_success: Mapped[float | None] = mapped_column(nullable=True)
    average_points: Mapped[float | None] = mapped_column(nullable=True)
    dnf_rate: Mapped[float | None] = mapped_column(nullable=True)
    development_index: Mapped[float | None] = mapped_column(nullable=True)
    average_pace: Mapped[float | None] = mapped_column(nullable=True)
