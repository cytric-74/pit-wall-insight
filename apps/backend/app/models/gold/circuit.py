"""`dim_circuit` — one row per circuit (docs/07_DATABASE_SCHEMA.md).

`circuit_id` is the *same* UUID as the corresponding `raw_circuits.id` row
— see `DimConstructor` for why that matters. `latitude`/`longitude` are
parsed to `Float` here (Bronze keeps Jolpica's raw coordinate strings
as-is). `length`/`corners`/`drs_zones`/`lap_record`/`clockwise`/`svg_track`
have no source in this pipeline at all (no collected data covers them yet)
and are left `NULL` rather than fabricated — populating them would require
either a manual reference table or a future data source this project
doesn't have.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import GoldBase
from app.models.mixins import GoldAuditMixin


class DimCircuit(GoldBase, GoldAuditMixin):
    __tablename__ = "dim_circuit"

    circuit_id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    country: Mapped[str | None] = mapped_column(nullable=True)
    city: Mapped[str | None] = mapped_column(nullable=True)
    length: Mapped[float | None] = mapped_column(nullable=True)
    corners: Mapped[int | None] = mapped_column(nullable=True)
    drs_zones: Mapped[int | None] = mapped_column(nullable=True)
    lap_record: Mapped[str | None] = mapped_column(nullable=True)
    clockwise: Mapped[bool | None] = mapped_column(nullable=True)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    svg_track: Mapped[str | None] = mapped_column(nullable=True)
