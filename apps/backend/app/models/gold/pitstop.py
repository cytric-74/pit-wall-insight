"""`fct_pitstop` — one row per detected pit stop (docs/07_DATABASE_SCHEMA.md).

Derived from `raw_laps` rows where both `pit_in_time` and `pit_out_time`
are populated *on the same lap row* — FastF1 reports a stop this way when
the in-lap and out-lap are the same recorded lap. A stop that spans two
separate lap rows (pit entry recorded on one lap, exit on the next) is not
currently detected — a known, documented limitation of this simplified
approach rather than an attempt at fragile cross-row matching. `pit_duration`
is `pit_out_time - pit_in_time` (both already in seconds).
`compound_before`/`compound_after` come from the immediately preceding and
current lap's `compound` for that driver; `stop_number` is a simple 1-based
count of stops for that driver within the session, in lap order.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import GoldBase
from app.models.mixins import GoldAuditMixin


class FctPitstop(GoldBase, GoldAuditMixin):
    __tablename__ = "fct_pitstop"
    __table_args__ = (
        UniqueConstraint("session_id", "driver_id", "lap", name="uq_fct_pitstop_natural_key"),
    )

    pitstop_id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    driver_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("dim_driver.driver_id"), nullable=False, index=True
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("dim_session.session_id"), nullable=False, index=True
    )
    lap: Mapped[float] = mapped_column(nullable=False)
    pit_duration: Mapped[float | None] = mapped_column(nullable=True)
    stop_number: Mapped[int | None] = mapped_column(nullable=True)
    compound_before: Mapped[str | None] = mapped_column(nullable=True)
    compound_after: Mapped[str | None] = mapped_column(nullable=True)
