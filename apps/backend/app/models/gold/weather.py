"""`dim_weather` — one row per session's weather summary (docs/07_DATABASE_SCHEMA.md).

Grain: **one row per session**, not one row per FastF1 weather sample.
docs/07_DATABASE_SCHEMA.md's entity relationship diagram shows `dim_session`
holding a single `weather_id` foreign key — a dimension, not a time series —
so the transformer aggregates every `raw_weather` sample for a session
(FastF1 samples roughly once a minute) into one representative row:
averages for temperature/humidity/pressure/wind speed, the most common wind
direction, and whether rain was recorded at all during the session. This is
real Gold-layer analytical work (an aggregation), unlike Bronze's raw
passthrough — see `apps/ingestion/transformers/bronze_to_gold.py` for the
exact aggregation. `track_status` has no source in this pipeline (FastF1's
track status codes weren't collected in Phase 1) and is left `NULL`.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import GoldBase
from app.models.mixins import GoldAuditMixin


class DimWeather(GoldBase, GoldAuditMixin):
    __tablename__ = "dim_weather"

    weather_id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    air_temperature: Mapped[float | None] = mapped_column(nullable=True)
    track_temperature: Mapped[float | None] = mapped_column(nullable=True)
    humidity: Mapped[float | None] = mapped_column(nullable=True)
    wind_speed: Mapped[float | None] = mapped_column(nullable=True)
    wind_direction: Mapped[float | None] = mapped_column(nullable=True)
    rainfall: Mapped[bool | None] = mapped_column(nullable=True)
    pressure: Mapped[float | None] = mapped_column(nullable=True)
    track_status: Mapped[str | None] = mapped_column(nullable=True)
