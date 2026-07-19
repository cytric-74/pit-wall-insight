"""`raw_drivers` — one row per distinct driver encountered (docs/07_DATABASE_SCHEMA.md).

Sourced from Jolpica-F1's nested `Driver` object, embedded inside both
driver standings and race results (`RawDriverRef` in
`apps/ingestion/validators/schema.py`). FastF1's session results identify
drivers only by `DriverNumber`/`Abbreviation` (no stable cross-season
natural key equivalent to Jolpica's `driverId`), so this table is
populated from Jolpica records only in this phase — FastF1-sourced tables
(`RawResult`, `RawLap`) reference drivers via their own source's local
identifier (see `RawResult.driver_ref`, `RawLap.driver_ref`) rather than a
foreign key into this table; reconciling the two identifier systems into
one canonical driver reference is Gold-layer work for a future phase.
"""

from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.raw.mixins import AuditMixin


class RawDriver(Base, AuditMixin):
    __tablename__ = "raw_drivers"

    # Natural key: Jolpica's `driverId` (e.g. "max_verstappen").
    driver_id: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    # The 3-letter code (e.g. "VER") FastF1 also uses — `None` for many
    # pre-2014 drivers, per RawDriverRef's own documented edge case.
    code: Mapped[str | None] = mapped_column(nullable=True)
    given_name: Mapped[str] = mapped_column(nullable=False)
    family_name: Mapped[str] = mapped_column(nullable=False)
    date_of_birth: Mapped[str | None] = mapped_column(nullable=True)
    nationality: Mapped[str | None] = mapped_column(nullable=True)
