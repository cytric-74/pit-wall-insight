"""`dim_season` — one row per Formula One season (docs/07_DATABASE_SCHEMA.md).

Derived by the transformer from the distinct `season` values it finds in
Bronze (`raw_sessions`/`raw_results`), not copied from any single raw
table — there is no `raw_seasons` table (see `app/models/raw/__init__.py`
for why). `race_count`/`sprint_count` are counted from `raw_sessions`;
`champion_driver`/`champion_constructor` are resolved from whichever
driver/constructor ranked position `1` in that season's final standings
(only meaningful once a season's data is complete — see the transformer
for how an in-progress season is handled).

`champion_driver_id`/`champion_constructor_id` are the FK-based source of
truth for the same fact — `champion_driver`/`champion_constructor` are
display-name strings only, and two drivers sharing an identical full name
(or a later name correction) would silently misattribute anything matched
against them by string (Phase 7 audit, Critical). Nullable and additive:
existing name columns are unchanged, so nothing that reads them breaks.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import GoldBase
from app.models.mixins import GoldAuditMixin


class DimSeason(GoldBase, GoldAuditMixin):
    __tablename__ = "dim_season"

    season_id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    year: Mapped[int] = mapped_column(unique=True, nullable=False, index=True)
    race_count: Mapped[int] = mapped_column(nullable=False)
    sprint_count: Mapped[int | None] = mapped_column(nullable=True)
    champion_driver: Mapped[str | None] = mapped_column(nullable=True)
    champion_constructor: Mapped[str | None] = mapped_column(nullable=True)
    champion_driver_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(), ForeignKey("dim_driver.driver_id"), nullable=True
    )
    champion_constructor_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(), ForeignKey("dim_constructor.constructor_id"), nullable=True
    )
