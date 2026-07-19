"""add raw_results driver_code and constructor_ref

Revision ID: 78d373297f62
Revises: bc6a4663b61a
Create Date: 2026-07-19 20:55:22.472962

Additive-only migration, surfaced by the Gold-layer transform (Phase 3):
reconciling a FastF1-sourced `raw_results` row back to `raw_drivers`/
`raw_constructors` (both Jolpica-keyed) needs FastF1's own driver
abbreviation and team name, which Phase 2's original `raw_results` didn't
capture. See `app/models/raw/result.py` for the full rationale. Existing
rows get `NULL` in both new columns until re-ingested — safe, since both
are nullable and no existing code reads them yet.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "78d373297f62"
down_revision: str | None = "bc6a4663b61a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("raw_results", sa.Column("driver_code", sa.String(), nullable=True))
    op.add_column("raw_results", sa.Column("constructor_ref", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("raw_results", "constructor_ref")
    op.drop_column("raw_results", "driver_code")
