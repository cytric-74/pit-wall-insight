"""`raw_results` — one row per driver's classification in one session (docs/07_DATABASE_SCHEMA.md).

Both FastF1 session results (`RawSessionResult`) and Jolpica race results
(`RawRaceResult`) land here, distinguished by `source` — never merged (see
`app/models/raw/__init__.py`). `driver_ref` is deliberately a plain string
rather than a foreign key into `RawDriver`: FastF1 identifies a driver by
`DriverNumber` (e.g. `"1"`) and Jolpica by `driverId` (e.g.
`"max_verstappen"`) — two different identifier systems that this Bronze
table does not attempt to reconcile. A future Gold-layer transform is
where "which `RawDriver` row does this `driver_ref` actually mean" gets
resolved, once both sources' naming can be cross-referenced against known
mappings.
"""

from __future__ import annotations

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.raw.mixins import AuditMixin


class RawResult(Base, AuditMixin):
    __tablename__ = "raw_results"
    __table_args__ = (
        UniqueConstraint(
            "source",
            "season",
            "round_number",
            "session_type",
            "driver_ref",
            name="uq_raw_results_natural_key",
        ),
    )

    season: Mapped[int] = mapped_column(nullable=False, index=True)
    round_number: Mapped[int] = mapped_column(nullable=False)
    # "R" for every Jolpica row (Jolpica only ever reports race results);
    # FastF1 rows carry whichever session type was actually requested
    # (FP1/FP2/FP3/Q/S/SQ/R).
    session_type: Mapped[str] = mapped_column(nullable=False)
    driver_ref: Mapped[str] = mapped_column(nullable=False, index=True)
    position: Mapped[float | None] = mapped_column(nullable=True)
    points: Mapped[float | None] = mapped_column(nullable=True)
    status: Mapped[str | None] = mapped_column(nullable=True)
    grid_position: Mapped[float | None] = mapped_column(nullable=True)
