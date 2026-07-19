"""`raw_results` — one row per driver's classification in one session (docs/07_DATABASE_SCHEMA.md).

Both FastF1 session results (`RawSessionResult`) and Jolpica race results
(`RawRaceResult`) land here, distinguished by `source` — never merged (see
`app/models/raw/__init__.py`). `driver_ref` is deliberately a plain string
rather than a foreign key into `RawDriver`: FastF1 identifies a driver by
`DriverNumber` (e.g. `"1"`) and Jolpica by `driverId` (e.g.
`"max_verstappen"`) — two different identifier systems that this Bronze
table does not attempt to reconcile.

`driver_code` and `constructor_ref` (added in migration
`a1f2c9e6d3b7_add_raw_results_driver_code_and_constructor_ref.py`, once the
Gold-layer transform needed them) exist purely to make that reconciliation
*possible* for a future consumer, without this table performing it itself:

- `driver_code`: FastF1's `Abbreviation` (e.g. `"VER"`) — matches
  `RawDriver.code` exactly, giving the Gold transform a reliable join key
  from a FastF1-sourced row back to `RawDriver` (whose `driver_id` natural
  key is Jolpica's `driverId`, which FastF1 rows have no direct equivalent
  of). `None` for Jolpica-sourced rows, since `driver_ref` already *is*
  `driverId` there — no reconciliation needed.
- `constructor_ref`: the team, as each source names it — Jolpica's
  `constructorId` (stable, exact-matches `RawConstructor.constructor_id`)
  or FastF1's `TeamName` (free text, no stable id at the results level;
  reconciling it is a best-effort string match, not an exact key).
"""

from __future__ import annotations

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.mixins import AuditMixin


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
    driver_code: Mapped[str | None] = mapped_column(nullable=True)
    constructor_ref: Mapped[str | None] = mapped_column(nullable=True)
