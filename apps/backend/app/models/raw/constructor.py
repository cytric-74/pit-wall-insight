"""`raw_constructors` — one row per distinct constructor encountered (docs/07_DATABASE_SCHEMA.md).

Sourced from Jolpica-F1's nested `Constructor` object, embedded inside
constructor standings, driver standings (a driver's current team), and
race results (`RawConstructorRef` in `apps/ingestion/validators/schema.py`).
Same rationale as `RawDriver` for why FastF1 doesn't contribute here in
this phase: FastF1 identifies teams by `TeamName` text, not a stable id
comparable to Jolpica's `constructorId`.
"""

from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.mixins import AuditMixin


class RawConstructor(Base, AuditMixin):
    __tablename__ = "raw_constructors"

    # Natural key: Jolpica's `constructorId` (e.g. "red_bull").
    constructor_id: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    nationality: Mapped[str | None] = mapped_column(nullable=True)
