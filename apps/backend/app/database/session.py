"""SQLAlchemy 2.0 async engine, session factory, and declarative base.

No ORM models are defined yet — `app/models/` is intentionally empty until
the first domain model is designed. This module only wires up the plumbing
those models will eventually attach to.
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
    """Declarative base every future ORM model (`app/models/`) will inherit from."""


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a session against the raw/bronze database, one per request."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_analytics_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a session against the analytics/gold database, one per request."""
    async with AnalyticsAsyncSessionLocal() as session:
        yield session
