"""`dim_driver` — one row per driver (docs/07_DATABASE_SCHEMA.md).

`driver_id` is the *same* UUID as the corresponding `raw_drivers.id` row
(both derived via `utils.ids.generate_id("driver", driverId)`) — see
`DimConstructor` for why that matters. `date_of_birth` is parsed to a real
`Date` here (Bronze keeps it as the source's raw string, per "minimal
transformation, source aligned" — casting types is exactly the kind of
work that belongs to this Gold transform instead).

`rookie_season` and `world_titles` are computed by the transformer by
scanning every season currently loaded into Bronze/Gold (respectively:
the earliest season this driver appears in at all, and how many
`dim_season` rows name this driver as `champion_driver`) — both are only
as complete as the data loaded so far, and will read low for a driver
whose earlier seasons haven't been ingested yet. `active` reflects whether
this driver appears in the most recently loaded season.
"""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import GoldBase
from app.models.mixins import GoldAuditMixin


class DimDriver(GoldBase, GoldAuditMixin):
    __tablename__ = "dim_driver"

    driver_id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    driver_number: Mapped[int | None] = mapped_column(nullable=True)
    full_name: Mapped[str] = mapped_column(nullable=False)
    abbreviation: Mapped[str | None] = mapped_column(nullable=True)
    nationality: Mapped[str | None] = mapped_column(nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(nullable=True)
    team_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(), ForeignKey("dim_constructor.constructor_id"), nullable=True
    )
    rookie_season: Mapped[int | None] = mapped_column(nullable=True)
    world_titles: Mapped[int | None] = mapped_column(nullable=True)
    active: Mapped[bool | None] = mapped_column(nullable=True)
