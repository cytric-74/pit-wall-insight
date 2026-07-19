"""`fct_results` — one row per driver's classification in one session (docs/07_DATABASE_SCHEMA.md).

Unlike Bronze's `raw_results` (which keeps FastF1 and Jolpica rows
separate, tagged by `source`), this table reconciles them: per the
source-of-truth plan for this pipeline, a FastF1-sourced row is preferred
whenever one exists for a given (season, round, session_type, driver), and
a Jolpica-sourced row is used only as a fallback (for seasons or session
types FastF1 doesn't cover). There is exactly one `fct_results` row per
driver per session, never two.

`fastest_lap` and `laps_completed` are computed by the transformer from
`fct_laps` (whichever driver has the minimum `lap_time` in a session is
flagged; `laps_completed` is that driver's row count in `fct_laps` for the
session) — both `NULL` when no lap data exists for the session (e.g. a
Jolpica-only historical season).
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import GoldBase
from app.models.mixins import GoldAuditMixin


class FctResult(GoldBase, GoldAuditMixin):
    __tablename__ = "fct_results"
    __table_args__ = (
        UniqueConstraint("session_id", "driver_id", name="uq_fct_results_natural_key"),
    )

    result_id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    driver_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("dim_driver.driver_id"), nullable=False, index=True
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("dim_session.session_id"), nullable=False, index=True
    )
    grid_position: Mapped[float | None] = mapped_column(nullable=True)
    finish_position: Mapped[float | None] = mapped_column(nullable=True)
    points: Mapped[float | None] = mapped_column(nullable=True)
    status: Mapped[str | None] = mapped_column(nullable=True)
    fastest_lap: Mapped[bool | None] = mapped_column(nullable=True)
    laps_completed: Mapped[int | None] = mapped_column(nullable=True)
