"""Alembic migration environment for the analytics/Gold database.

A second, independent migration history from `alembic/` (which targets the
raw/Bronze database) — see `app/database/session.py`'s module docstring for
why Raw and Gold use two separate declarative bases (`Base`/`GoldBase`) in
the first place: they're two different physical PostgreSQL databases
(`pit_wall_insight_raw` vs `pit_wall_insight_analytics`), so each needs its
own migration history rather than sharing one `alembic/versions/` directory
that would otherwise mix DDL for two unrelated databases together.

Run with `alembic -c alembic_gold.ini <command>` (as opposed to plain
`alembic <command>`, which uses `alembic.ini` / this file's sibling
`alembic/env.py` for the raw database).
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# Importing app.models populates GoldBase.metadata (alongside Base's) as a
# side effect — see that package's docstring.
import app.models  # noqa: F401
from alembic import context
from app.core.config import get_settings
from app.database.session import GoldBase

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = GoldBase.metadata

settings = get_settings()


def run_migrations_offline() -> None:
    """Generate SQL scripts without a live database connection."""
    context.configure(
        url=settings.analytics_sqlalchemy_database_uri,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable: AsyncEngine = create_async_engine(settings.analytics_sqlalchemy_database_uri)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
