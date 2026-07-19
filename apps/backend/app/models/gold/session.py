"""`dim_session` — one row per (season, round, session type) actually recorded (docs/07_DATABASE_SCHEMA.md).

Grain note: Bronze's `raw_sessions` is at *round* grain (one row per race
weekend, per source — see `app/models/raw/session.py`), not per individual
session type. `dim_session`'s real per-session-type grain (FP1/FP2/FP3/Q/
S/SQ/R) is derived instead from the distinct `(season, round_number,
session_type)` combinations the transformer finds across `raw_results`,
`raw_laps`, and `raw_weather` — every one of those Bronze tables already
carries `session_type` at the row level, since they're FastF1-sourced
facts scoped to one specific session.

`circuit_id` is resolved by matching a round's `raw_sessions` (Jolpica)
`location`/`country` text against `raw_circuits.locality`/`country` — a
best-effort string match, since Bronze doesn't carry a direct
round-to-circuit foreign key (see `app/models/raw/session.py`). It's
`NULL` when no match is found rather than a guess.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import GoldBase
from app.models.mixins import GoldAuditMixin


class DimSession(GoldBase, GoldAuditMixin):
    __tablename__ = "dim_session"
    __table_args__ = (
        UniqueConstraint(
            "season_id", "round_number", "session_type", name="uq_dim_session_natural_key"
        ),
    )

    session_id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    season_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("dim_season.season_id"), nullable=False, index=True
    )
    round_number: Mapped[int] = mapped_column(nullable=False)
    race_name: Mapped[str | None] = mapped_column(nullable=True)
    session_type: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[str | None] = mapped_column(nullable=True)
    weather_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(), ForeignKey("dim_weather.weather_id"), nullable=True
    )
    circuit_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(), ForeignKey("dim_circuit.circuit_id"), nullable=True
    )
