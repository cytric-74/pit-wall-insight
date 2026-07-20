"""add dim_season champion_driver_id and champion_constructor_id

Revision ID: 1f6c8a9b3d2e
Revises: 40170f70a823
Create Date: 2026-07-21 00:00:00.000000

Additive-only migration (Phase 7 audit, Critical): `dim_season.champion_driver`/
`champion_constructor` are display-name strings, and `_finalize_driver_world_titles`
(apps/ingestion/transformers/bronze_to_gold.py) matched them back to
`dim_driver` by name string — two drivers sharing an identical full name, or
a later name correction, would silently misattribute championship counts.
These two nullable FK columns are the ID-based source of truth for the same
fact; the existing name columns are untouched, so nothing that reads them
breaks. Existing rows get `NULL` until re-transformed.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1f6c8a9b3d2e"
down_revision: str | None = "40170f70a823"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("dim_season", sa.Column("champion_driver_id", sa.Uuid(), nullable=True))
    op.add_column("dim_season", sa.Column("champion_constructor_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_dim_season_champion_driver_id",
        "dim_season",
        "dim_driver",
        ["champion_driver_id"],
        ["driver_id"],
    )
    op.create_foreign_key(
        "fk_dim_season_champion_constructor_id",
        "dim_season",
        "dim_constructor",
        ["champion_constructor_id"],
        ["constructor_id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_dim_season_champion_constructor_id", "dim_season", type_="foreignkey")
    op.drop_constraint("fk_dim_season_champion_driver_id", "dim_season", type_="foreignkey")
    op.drop_column("dim_season", "champion_constructor_id")
    op.drop_column("dim_season", "champion_driver_id")
