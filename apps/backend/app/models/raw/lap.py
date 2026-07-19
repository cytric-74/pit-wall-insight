"""`raw_laps` — one row per driver's one lap in one session (docs/07_DATABASE_SCHEMA.md).

FastF1-only: lap-by-lap granularity does not exist in Jolpica at all, for
any season (see `apps/ingestion/collectors/fastf1_client.py`'s module
docstring). `driver_ref` here is FastF1's `Driver` abbreviation
(e.g. `"VER"`), not Jolpica's `driverId` — the same "no cross-source
reconciliation at Bronze" rationale as `RawResult.driver_ref`.

`pit_in_time`/`pit_out_time` being non-`None` together on the same row
identifies a pit-stop lap. There is no separate `raw_pitstops` table in
this phase (see `app/models/raw/__init__.py`) — a future Gold-layer
transform derives `fct_pitstop` directly from these two columns, since no
independent pit-stop data source exists to load into a Bronze table of its
own.
"""

from __future__ import annotations

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.mixins import AuditMixin


class RawLap(Base, AuditMixin):
    __tablename__ = "raw_laps"
    __table_args__ = (
        UniqueConstraint(
            "source",
            "season",
            "round_number",
            "session_type",
            "driver_ref",
            "lap_number",
            name="uq_raw_laps_natural_key",
        ),
    )

    season: Mapped[int] = mapped_column(nullable=False, index=True)
    round_number: Mapped[int] = mapped_column(nullable=False)
    session_type: Mapped[str] = mapped_column(nullable=False)
    driver_ref: Mapped[str] = mapped_column(nullable=False, index=True)
    lap_number: Mapped[float] = mapped_column(nullable=False)
    lap_time: Mapped[float | None] = mapped_column(nullable=True)
    sector_1_time: Mapped[float | None] = mapped_column(nullable=True)
    sector_2_time: Mapped[float | None] = mapped_column(nullable=True)
    sector_3_time: Mapped[float | None] = mapped_column(nullable=True)
    compound: Mapped[str | None] = mapped_column(nullable=True)
    tyre_life: Mapped[float | None] = mapped_column(nullable=True)
    stint: Mapped[float | None] = mapped_column(nullable=True)
    pit_in_time: Mapped[float | None] = mapped_column(nullable=True)
    pit_out_time: Mapped[float | None] = mapped_column(nullable=True)
    position: Mapped[float | None] = mapped_column(nullable=True)
