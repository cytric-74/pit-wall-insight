"""add pg_trgm GIN indexes for search columns

Revision ID: 2a7d5e91c4f0
Revises: 1f6c8a9b3d2e
Create Date: 2026-07-21 00:00:00.000000

Additive-only migration (Phase 7 audit, Medium): `/search`
(app/repositories/search_repository.py) matches every column with a
leading-wildcard `func.lower(column).like(f"%{query}%")` — a pattern no
standard B-tree index can ever use. Postgres's `pg_trgm` extension plus a
GIN index on the same `lower(column)` expression the query already filters
on is what actually accelerates this; fine at current data volumes, but
degrades linearly as seasons/drivers/races accumulate, on an endpoint with
no rate limit (see the Critical/High rate-limiting findings).

Postgres-only (`CREATE EXTENSION`/`gin_trgm_ops` have no SQLite
equivalent, but this project's tests run the Gold layer against SQLite —
see other migrations' rationale for the same split) — verified via
Alembic's offline SQL-generation mode against the configured Postgres URL,
not against the SQLite test suite.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2a7d5e91c4f0"
down_revision: str | None = "1f6c8a9b3d2e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_INDEXES = (
    ("ix_dim_driver_full_name_trgm", "dim_driver", "full_name"),
    ("ix_dim_constructor_team_name_trgm", "dim_constructor", "team_name"),
    ("ix_dim_circuit_name_trgm", "dim_circuit", "name"),
    ("ix_dim_session_race_name_trgm", "dim_session", "race_name"),
)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    for index_name, table_name, column_name in _INDEXES:
        op.execute(
            f"CREATE INDEX {index_name} ON {table_name} "
            f"USING GIN (lower({column_name}) gin_trgm_ops)"
        )


def downgrade() -> None:
    for index_name, _table_name, _column_name in reversed(_INDEXES):
        op.execute(f"DROP INDEX IF EXISTS {index_name}")
