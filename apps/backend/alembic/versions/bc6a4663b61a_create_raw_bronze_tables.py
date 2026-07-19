"""create raw bronze tables

Revision ID: bc6a4663b61a
Revises:
Create Date: 2026-07-19 20:24:48.213688

Creates the Bronze layer (docs/06_DATA_ENGINEERING.md, docs/07_DATABASE_SCHEMA.md):
`raw_circuits`, `raw_drivers`, `raw_constructors`, `raw_sessions`,
`raw_results`, `raw_laps`, `raw_weather`. Column definitions here are
hand-written to mirror `app/models/raw/*.py` exactly (rather than produced
via `alembic revision --autogenerate`, which needs a live database
connection to diff against — unavailable in this project's current
environment). Every table carries the same four audit columns
(`app/models/raw/mixins.py::AuditMixin`) plus a UUID primary key that
`apps/ingestion`'s loaders populate deterministically
(`apps/ingestion/utils/ids.py::generate_id`) rather than a database-side
default — hence no `server_default` on `id` here.

No `naming_convention` is configured on this project's `Base.metadata`
(see `app/database/session.py`), so constraint names are given as explicit
string literals here rather than via Alembic's `op.f()` helper (which
requires a naming convention to resolve its format tokens against).
"""

from collections.abc import Sequence
from typing import Any

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bc6a4663b61a"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _audit_columns() -> list[sa.Column[Any]]:
    """The four columns every raw_* table shares, per `AuditMixin`.

    Factored out so each `op.create_table` call below reads as "id + audit
    columns + this table's own columns" rather than repeating the same five
    `sa.Column(...)` lines seven times with room for one of them to
    silently drift from the others.
    """
    return [
        sa.Column("id", sa.Uuid(), nullable=False),
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
        "raw_circuits",
        *_audit_columns(),
        sa.Column("circuit_id", sa.String(), nullable=False),
        sa.Column("circuit_name", sa.String(), nullable=False),
        sa.Column("locality", sa.String(), nullable=True),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("latitude", sa.String(), nullable=True),
        sa.Column("longitude", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_raw_circuits_circuit_id", "raw_circuits", ["circuit_id"], unique=True
    )

    op.create_table(
        "raw_drivers",
        *_audit_columns(),
        sa.Column("driver_id", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=True),
        sa.Column("given_name", sa.String(), nullable=False),
        sa.Column("family_name", sa.String(), nullable=False),
        sa.Column("date_of_birth", sa.String(), nullable=True),
        sa.Column("nationality", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_raw_drivers_driver_id", "raw_drivers", ["driver_id"], unique=True)

    op.create_table(
        "raw_constructors",
        *_audit_columns(),
        sa.Column("constructor_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("nationality", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_raw_constructors_constructor_id", "raw_constructors", ["constructor_id"], unique=True
    )

    op.create_table(
        "raw_sessions",
        *_audit_columns(),
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("race_name", sa.String(), nullable=True),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("event_date", sa.String(), nullable=True),
        sa.Column("f1_api_support", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source", "season", "round_number", name="uq_raw_sessions_natural_key"
        ),
    )
    op.create_index("ix_raw_sessions_season", "raw_sessions", ["season"])

    op.create_table(
        "raw_results",
        *_audit_columns(),
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("session_type", sa.String(), nullable=False),
        sa.Column("driver_ref", sa.String(), nullable=False),
        sa.Column("position", sa.Float(), nullable=True),
        sa.Column("points", sa.Float(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("grid_position", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source",
            "season",
            "round_number",
            "session_type",
            "driver_ref",
            name="uq_raw_results_natural_key",
        ),
    )
    op.create_index("ix_raw_results_season", "raw_results", ["season"])
    op.create_index("ix_raw_results_driver_ref", "raw_results", ["driver_ref"])

    op.create_table(
        "raw_laps",
        *_audit_columns(),
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("session_type", sa.String(), nullable=False),
        sa.Column("driver_ref", sa.String(), nullable=False),
        sa.Column("lap_number", sa.Float(), nullable=False),
        sa.Column("lap_time", sa.Float(), nullable=True),
        sa.Column("sector_1_time", sa.Float(), nullable=True),
        sa.Column("sector_2_time", sa.Float(), nullable=True),
        sa.Column("sector_3_time", sa.Float(), nullable=True),
        sa.Column("compound", sa.String(), nullable=True),
        sa.Column("tyre_life", sa.Float(), nullable=True),
        sa.Column("stint", sa.Float(), nullable=True),
        sa.Column("pit_in_time", sa.Float(), nullable=True),
        sa.Column("pit_out_time", sa.Float(), nullable=True),
        sa.Column("position", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source",
            "season",
            "round_number",
            "session_type",
            "driver_ref",
            "lap_number",
            name="uq_raw_laps_natural_key",
        ),
    )
    op.create_index("ix_raw_laps_season", "raw_laps", ["season"])
    op.create_index("ix_raw_laps_driver_ref", "raw_laps", ["driver_ref"])

    op.create_table(
        "raw_weather",
        *_audit_columns(),
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("session_type", sa.String(), nullable=False),
        sa.Column("time_offset_seconds", sa.Float(), nullable=False),
        sa.Column("air_temp", sa.Float(), nullable=True),
        sa.Column("track_temp", sa.Float(), nullable=True),
        sa.Column("humidity", sa.Float(), nullable=True),
        sa.Column("pressure", sa.Float(), nullable=True),
        sa.Column("wind_direction", sa.Float(), nullable=True),
        sa.Column("wind_speed", sa.Float(), nullable=True),
        sa.Column("rainfall", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source",
            "season",
            "round_number",
            "session_type",
            "time_offset_seconds",
            name="uq_raw_weather_natural_key",
        ),
    )
    op.create_index("ix_raw_weather_season", "raw_weather", ["season"])


def downgrade() -> None:
    # Reverse order of creation, since none of these tables have foreign
    # keys between them (Bronze deliberately doesn't enforce cross-table
    # referential integrity — see app/models/raw/__init__.py), the drop
    # order isn't load-bearing, but reversing it is the conventional,
    # least-surprising choice for anyone reading this file top to bottom.
    op.drop_table("raw_weather")
    op.drop_table("raw_laps")
    op.drop_table("raw_results")
    op.drop_table("raw_sessions")
    op.drop_table("raw_constructors")
    op.drop_table("raw_drivers")
    op.drop_table("raw_circuits")
