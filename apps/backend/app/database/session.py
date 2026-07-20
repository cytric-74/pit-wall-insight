"""SQLAlchemy 2.0 async engines, session factories, and declarative bases.

Two of each — one per physical database (raw/bronze, analytics/gold) — so
`app/models/raw/*.py` and `app/models/gold/*.py` each attach to the
metadata for the database they actually belong to. Mixing them into one
`Base`/`metadata` would let Alembic's autogenerate (or `create_all`) try to
create Bronze tables in the Gold database or vice versa; keeping them
separate is what makes `alembic/` (raw) and `alembic_gold/` (gold) two
independent migration histories, matching docs/06_DATA_ENGINEERING.md
Decision 005 ("API Reads Only Gold Models").
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

engine: AsyncEngine = create_async_engine(
    settings.sqlalchemy_database_uri,
    echo=settings.is_development,
    pool_pre_ping=True,
)

# Separate engine for the analytics/gold layer the API actually reads from
# (see docs/06_DATA_ENGINEERING.md — "API Reads Only Gold Models").
analytics_engine: AsyncEngine = create_async_engine(
    settings.analytics_sqlalchemy_database_uri,
    echo=settings.is_development,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
AnalyticsAsyncSessionLocal = async_sessionmaker(
    bind=analytics_engine, expire_on_commit=False, autoflush=False
)


class Base(DeclarativeBase):
    """Declarative base for every Bronze (`raw_*`) model (`app/models/raw/`)."""


class GoldBase(DeclarativeBase):
    """Declarative base for every Gold (`dim_*`/`fct_*`) model (`app/models/gold/`).

    A separate class (not just a second `metadata`) because SQLAlchemy
    resolves relationships/foreign keys within one declarative base's
    registry — Gold models reference each other (e.g. `FctResult.driver_id`
    -> `DimDriver.driver_id`) and must never accidentally resolve against a
    Bronze table of a similar name.
    """


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a session against the raw/bronze database, one per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_analytics_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a session against the analytics/gold database, one per request."""
    async with AnalyticsAsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
