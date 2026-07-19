"""`raw_circuits` — one row per distinct circuit encountered (docs/07_DATABASE_SCHEMA.md).

Sourced from Jolpica-F1's nested `Circuit` object, embedded inside every
season calendar entry (`RawRaceCalendarEntry.Circuit` in
`apps/ingestion/validators/schema.py`). FastF1 does not currently
contribute to this table in this phase — its event schedule identifies
circuits by `Location`/`Country` text fields rather than a stable circuit
id, so there is no reliable natural key to upsert on from that source yet.

Latitude/longitude are stored as the strings Jolpica sends (e.g.
`"26.0325"`), not parsed to `Float` — per Bronze's "minimal transformation,
source aligned" philosophy, casting to a numeric type is Silver-layer work
for a future phase, not this one's.
"""

from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.mixins import AuditMixin


class RawCircuit(Base, AuditMixin):
    __tablename__ = "raw_circuits"

    # Natural key: Jolpica's `circuitId` (e.g. "bahrain"). Unique so
    # re-ingesting the same circuit (seen across many seasons' calendars)
    # upserts the same row rather than duplicating it.
    circuit_id: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    circuit_name: Mapped[str] = mapped_column(nullable=False)
    locality: Mapped[str | None] = mapped_column(nullable=True)
    country: Mapped[str | None] = mapped_column(nullable=True)
    latitude: Mapped[str | None] = mapped_column(nullable=True)
    longitude: Mapped[str | None] = mapped_column(nullable=True)
