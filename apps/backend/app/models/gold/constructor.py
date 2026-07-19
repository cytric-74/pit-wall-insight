"""`dim_constructor` — one row per constructor (docs/07_DATABASE_SCHEMA.md: "Provides UI theming").

`constructor_id` is the *same* UUID as the corresponding `raw_constructors.id`
row — both are derived via `utils.ids.generate_id("constructor", constructorId)`,
so Bronze and Gold rows for the same constructor share an id without any
join/lookup being needed. `team_name`/`nationality` copy straight across
from `raw_constructors`; `team_principal`/`power_unit`/`primary_color`/
`secondary_color`/`logo`/`car_image` have no source in this pipeline at all
(no collected data covers them — the frontend currently hardcodes team
colors client-side in `packages/ui/src/theme/constructors.ts`) and are left
`NULL` rather than fabricated. `active` is derived by the transformer from
whether this constructor appears in the most recent season loaded into
Bronze.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import GoldBase
from app.models.mixins import GoldAuditMixin


class DimConstructor(GoldBase, GoldAuditMixin):
    __tablename__ = "dim_constructor"

    constructor_id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True)
    team_name: Mapped[str] = mapped_column(nullable=False)
    base_country: Mapped[str | None] = mapped_column(nullable=True)
    team_principal: Mapped[str | None] = mapped_column(nullable=True)
    power_unit: Mapped[str | None] = mapped_column(nullable=True)
    primary_color: Mapped[str | None] = mapped_column(nullable=True)
    secondary_color: Mapped[str | None] = mapped_column(nullable=True)
    logo: Mapped[str | None] = mapped_column(nullable=True)
    car_image: Mapped[str | None] = mapped_column(nullable=True)
    active: Mapped[bool | None] = mapped_column(nullable=True)
