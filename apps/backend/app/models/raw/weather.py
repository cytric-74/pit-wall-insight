"""`raw_weather` — one row per weather sample recorded during a session (docs/07_DATABASE_SCHEMA.md).

FastF1-only, like `RawLap` — Jolpica has no weather data at any grain.
`time_offset_seconds` is the sample's offset from session start (FastF1
reports weather `Time` as a `Timedelta` from session start, not a
wall-clock timestamp — see `fastf1_client.get_session_weather`), already
normalized to seconds by the collector layer before this table ever sees
it.
"""

from __future__ import annotations

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.raw.mixins import AuditMixin


class RawWeather(Base, AuditMixin):
    __tablename__ = "raw_weather"
    __table_args__ = (
        UniqueConstraint(
            "source",
            "season",
            "round_number",
            "session_type",
            "time_offset_seconds",
            name="uq_raw_weather_natural_key",
        ),
    )

    season: Mapped[int] = mapped_column(nullable=False, index=True)
    round_number: Mapped[int] = mapped_column(nullable=False)
    session_type: Mapped[str] = mapped_column(nullable=False)
    time_offset_seconds: Mapped[float] = mapped_column(nullable=False)
    air_temp: Mapped[float | None] = mapped_column(nullable=True)
    track_temp: Mapped[float | None] = mapped_column(nullable=True)
    humidity: Mapped[float | None] = mapped_column(nullable=True)
    pressure: Mapped[float | None] = mapped_column(nullable=True)
    wind_direction: Mapped[float | None] = mapped_column(nullable=True)
    wind_speed: Mapped[float | None] = mapped_column(nullable=True)
    rainfall: Mapped[bool | None] = mapped_column(nullable=True)
