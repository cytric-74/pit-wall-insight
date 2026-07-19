"""Sanity check that the Alembic migration file itself is valid.

Purpose
-------
`tests/test_raw_models.py` proves the ORM models (`app/models/raw/*.py`)
produce a working schema, but the migration file
(`alembic/versions/bc6a4663b61a_create_raw_bronze_tables.py`) is a
hand-written, separate artifact — the one Alembic actually runs against a
real Postgres database in every environment (dev, CI, production). Nothing
else in this test suite executes it. This test does, using Alembic's
"offline" mode (`alembic upgrade head --sql`), which renders the migration
to literal SQL text without opening a database connection at all — proving
the file imports cleanly, every `op.create_table`/`op.create_index` call is
well-formed, and the emitted SQL actually mentions every table this phase
adds.

Why offline mode specifically: this project's `alembic/env.py` /
`alembic_gold/env.py` always generate SQL against
`Settings.sqlalchemy_database_uri` /
`Settings.analytics_sqlalchemy_database_uri` (PostgreSQL URLs, even in
offline mode — the dialect determines SQL syntax, no connection is
opened), so this test exercises the exact PostgreSQL DDL a real deployment
would run, not a SQLite approximation of it.
"""

from __future__ import annotations

from pathlib import Path

from alembic.command import upgrade
from alembic.config import Config

_BACKEND_ROOT = Path(__file__).resolve().parents[1]


def test_offline_upgrade_emits_create_table_for_every_raw_table(capsys) -> None:  # type: ignore[no-untyped-def]
    config = Config(str(_BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(_BACKEND_ROOT / "alembic"))

    upgrade(config, "head", sql=True)

    emitted_sql = capsys.readouterr().out
    for table_name in (
        "raw_circuits",
        "raw_drivers",
        "raw_constructors",
        "raw_sessions",
        "raw_results",
        "raw_laps",
        "raw_weather",
    ):
        assert f"CREATE TABLE {table_name}" in emitted_sql, (
            f"Expected offline migration output to create {table_name}"
        )


def test_offline_gold_upgrade_emits_create_table_for_every_gold_table(capsys) -> None:  # type: ignore[no-untyped-def]
    config = Config(str(_BACKEND_ROOT / "alembic_gold.ini"))
    config.set_main_option("script_location", str(_BACKEND_ROOT / "alembic_gold"))

    upgrade(config, "head", sql=True)

    emitted_sql = capsys.readouterr().out
    for table_name in (
        "dim_season",
        "dim_constructor",
        "dim_circuit",
        "dim_weather",
        "dim_driver",
        "dim_session",
        "fct_results",
        "fct_laps",
        "fct_pitstop",
    ):
        assert f"CREATE TABLE {table_name}" in emitted_sql, (
            f"Expected offline gold migration output to create {table_name}"
        )
