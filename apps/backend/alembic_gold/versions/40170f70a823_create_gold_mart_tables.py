"""create gold mart tables

Revision ID: 40170f70a823
Revises: 8d4a909547da
Create Date: 2026-07-20 07:07:17.466264

Creates the Gold layer's marts (docs/07_DATABASE_SCHEMA.md):
`mart_dashboard`, `mart_driver_summary`, `mart_constructor_summary`,
`mart_race_summary` — hand-written to mirror `app/models/gold/mart_*.py`
exactly, for the same reason every other migration in this project is
(no live database to autogenerate against). All four depend on tables the
prior migration (`8d4a909547da`) already created (`dim_season`,
`dim_driver`, `dim_constructor`, `dim_session`), so this migration only
ever adds tables, never touches existing ones.
"""

from collections.abc import Sequence
from typing import Any

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "40170f70a823"
down_revision: str | None = "8d4a909547da"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _gold_audit_columns() -> list[sa.Column[Any]]:
    """See `alembic_gold/versions/8d4a909547da_...py` — identical helper,
    duplicated rather than imported across migration files, since Alembic
    migrations are meant to stand alone and remain readable/runnable in
    isolation, not depend on each other's internals."""
    return [
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("pipeline_version", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "mart_dashboard",
        sa.Column("season_id", sa.Uuid(), nullable=False),
        *_gold_audit_columns(),
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("drivers", sa.Integer(), nullable=False),
        sa.Column("constructors", sa.Integer(), nullable=False),
        sa.Column("races", sa.Integer(), nullable=False),
        sa.Column("fastest_pitstop", sa.Float(), nullable=True),
        sa.Column("average_overtakes", sa.Float(), nullable=True),
        sa.Column("fastest_lap_time", sa.Float(), nullable=True),
        sa.Column("fastest_lap_driver", sa.String(), nullable=True),
        sa.Column("championship_gap", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("season_id"),
        sa.ForeignKeyConstraint(["season_id"], ["dim_season.season_id"]),
    )

    op.create_table(
        "mart_driver_summary",
        sa.Column("mart_driver_summary_id", sa.Uuid(), nullable=False),
        *_gold_audit_columns(),
        sa.Column("season_id", sa.Uuid(), nullable=False),
        sa.Column("driver_id", sa.Uuid(), nullable=False),
        sa.Column("driver", sa.String(), nullable=False),
        sa.Column("wins", sa.Integer(), nullable=False),
        sa.Column("podiums", sa.Integer(), nullable=False),
        sa.Column("poles", sa.Integer(), nullable=False),
        sa.Column("fastest_laps", sa.Integer(), nullable=False),
        sa.Column("average_finish", sa.Float(), nullable=True),
        sa.Column("average_qualifying", sa.Float(), nullable=True),
        sa.Column("consistency_score", sa.Float(), nullable=True),
        sa.Column("pit_efficiency", sa.Float(), nullable=True),
        sa.Column("race_pace", sa.Float(), nullable=True),
        sa.Column("qualifying_pace", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("mart_driver_summary_id"),
        sa.ForeignKeyConstraint(["season_id"], ["dim_season.season_id"]),
        sa.ForeignKeyConstraint(["driver_id"], ["dim_driver.driver_id"]),
        sa.UniqueConstraint(
            "season_id", "driver_id", name="uq_mart_driver_summary_natural_key"
        ),
    )
    op.create_index(
        "ix_mart_driver_summary_season_id", "mart_driver_summary", ["season_id"]
    )
    op.create_index(
        "ix_mart_driver_summary_driver_id", "mart_driver_summary", ["driver_id"]
    )

    op.create_table(
        "mart_constructor_summary",
        sa.Column("mart_constructor_summary_id", sa.Uuid(), nullable=False),
        *_gold_audit_columns(),
        sa.Column("season_id", sa.Uuid(), nullable=False),
        sa.Column("constructor_id", sa.Uuid(), nullable=False),
        sa.Column("constructor", sa.String(), nullable=False),
        sa.Column("wins", sa.Integer(), nullable=False),
        sa.Column("podiums", sa.Integer(), nullable=False),
        sa.Column("pitstop_average", sa.Float(), nullable=True),
        sa.Column("strategy_success", sa.Float(), nullable=True),
        sa.Column("average_points", sa.Float(), nullable=True),
        sa.Column("dnf_rate", sa.Float(), nullable=True),
        sa.Column("development_index", sa.Float(), nullable=True),
        sa.Column("average_pace", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("mart_constructor_summary_id"),
        sa.ForeignKeyConstraint(["season_id"], ["dim_season.season_id"]),
        sa.ForeignKeyConstraint(["constructor_id"], ["dim_constructor.constructor_id"]),
        sa.UniqueConstraint(
            "season_id", "constructor_id", name="uq_mart_constructor_summary_natural_key"
        ),
    )
    op.create_index(
        "ix_mart_constructor_summary_season_id", "mart_constructor_summary", ["season_id"]
    )
    op.create_index(
        "ix_mart_constructor_summary_constructor_id", "mart_constructor_summary", ["constructor_id"]
    )

    op.create_table(
        "mart_race_summary",
        sa.Column("session_id", sa.Uuid(), nullable=False),
        *_gold_audit_columns(),
        sa.Column("race", sa.String(), nullable=True),
        sa.Column("winner", sa.String(), nullable=True),
        sa.Column("pole", sa.String(), nullable=True),
        sa.Column("fastest_lap", sa.String(), nullable=True),
        sa.Column("average_pitstop", sa.Float(), nullable=True),
        sa.Column("safety_car_laps", sa.Integer(), nullable=True),
        sa.Column("red_flags", sa.Integer(), nullable=True),
        sa.Column("weather", sa.String(), nullable=True),
        sa.Column("retirements", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("session_id"),
        sa.ForeignKeyConstraint(["session_id"], ["dim_session.session_id"]),
    )


def downgrade() -> None:
    op.drop_table("mart_race_summary")
    op.drop_table("mart_constructor_summary")
    op.drop_table("mart_driver_summary")
    op.drop_table("mart_dashboard")
