"""`fct_laps` — one row per driver's one lap in one session (docs/07_DATABASE_SCHEMA.md).

FastF1-only (Jolpica has no lap-level data), copied across from
`raw_laps` with `driver_ref` (FastF1's abbreviation) resolved to a real
`dim_driver.driver_id` via `raw_drivers.code`. `speed_trap` and `drs` have
no source in this pipeline — Phase 1's `RawSessionLap` validator schema
doesn't collect FastF1's speed-trap or DRS columns — and are left `NULL`
rather than fabricated. `pit_in`/`pit_out` are booleans derived from
whether `raw_laps.pit_in_time`/`pit_out_time` were populated on this lap.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import GoldBase
from app.models.mixins import GoldAuditMixin


class FctLap(GoldBase, GoldAuditMixin):
    __tablename__ = "fct_laps"
    __table_args__ = (
        UniqueConstraint(
            "session_id", "driver_id", "lap_number", name="uq_fct_laps_natural_key"
        ),
    )

    lap_id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    driver_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("dim_driver.driver_id"), nullable=False, index=True
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("dim_session.session_id"), nullable=False, index=True
    )
    lap_number: Mapped[float] = mapped_column(nullable=False)
    lap_time: Mapped[float | None] = mapped_column(nullable=True)
    sector_1: Mapped[float | None] = mapped_column(nullable=True)
    sector_2: Mapped[float | None] = mapped_column(nullable=True)
    sector_3: Mapped[float | None] = mapped_column(nullable=True)
    compound: Mapped[str | None] = mapped_column(nullable=True)
    tyre_life: Mapped[float | None] = mapped_column(nullable=True)
    position: Mapped[float | None] = mapped_column(nullable=True)
    speed_trap: Mapped[float | None] = mapped_column(nullable=True)
    drs: Mapped[bool | None] = mapped_column(nullable=True)
    pit_in: Mapped[bool | None] = mapped_column(nullable=True)
    pit_out: Mapped[bool | None] = mapped_column(nullable=True)
