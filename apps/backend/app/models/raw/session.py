"""`raw_sessions` — one row per event/round, per source (docs/07_DATABASE_SCHEMA.md).

Grain: one row per (`source`, `season`, `round_number`) — a full race
weekend, not an individual practice/qualifying/race sub-session. FastF1's
`RawEventSchedule` already carries its `Session1`..`Session5` names/dates as
flat columns on one weekend-level record rather than one row per session
slot; keeping this table at the same grain (rather than unpacking those
into separate rows) is a deliberate "minimal transformation" choice — any
unpacking is reshaping the source's own shape, which belongs to a future
Silver-layer `stg_sessions` model, not this Bronze table.

Both FastF1 (`RawEventSchedule`) and Jolpica (`RawRaceCalendarEntry`) rows
land here side by side, distinguished by `source` — see
`app/models/raw/__init__.py` for why Bronze never merges across sources.
`event_date` is stored as the ISO string/date each source provides,
unparsed, per Bronze's "source aligned" philosophy.
"""

from __future__ import annotations

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.raw.mixins import AuditMixin


class RawSession(Base, AuditMixin):
    __tablename__ = "raw_sessions"
    __table_args__ = (
        UniqueConstraint("source", "season", "round_number", name="uq_raw_sessions_natural_key"),
    )

    season: Mapped[int] = mapped_column(nullable=False, index=True)
    round_number: Mapped[int] = mapped_column(nullable=False)
    race_name: Mapped[str | None] = mapped_column(nullable=True)
    country: Mapped[str | None] = mapped_column(nullable=True)
    location: Mapped[str | None] = mapped_column(nullable=True)
    event_date: Mapped[str | None] = mapped_column(nullable=True)
    # FastF1-only: whether FastF1's live timing API has session-level data
    # for this event at all (see `fastf1_client.get_event_schedule`'s
    # docstring). Always `None` for Jolpica-sourced rows.
    f1_api_support: Mapped[bool | None] = mapped_column(nullable=True)
