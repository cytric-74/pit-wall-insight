"""Shared pytest fixtures."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database.session import GoldBase
from app.dependencies.database import get_analytics_db
from app.main import app


@pytest.fixture
async def analytics_engine() -> AsyncGenerator[AsyncEngine, None]:
    """A fresh in-memory SQLite database standing in for the analytics/gold
    database (no Postgres available in this environment — see
    `tests/test_gold_models.py` for the same rationale). Foreign keys are
    turned on explicitly, since SQLite ignores them by default.
    """
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    sync_engine = test_engine.sync_engine

    @event.listens_for(sync_engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection: object, _: object) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with test_engine.begin() as conn:
        await conn.run_sync(GoldBase.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest.fixture
def analytics_session_factory(
    analytics_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=analytics_engine, expire_on_commit=False, autoflush=False)


@pytest.fixture
async def client(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient, None]:
    """An HTTP client against the real FastAPI app, with `AnalyticsDbSession`
    overridden to the per-test in-memory database above — every API test
    seeds that same database (via `analytics_session_factory`) before
    issuing a request, rather than hitting a real Postgres connection.
    """

    async def _override_get_analytics_db() -> AsyncGenerator[AsyncSession, None]:
        async with analytics_session_factory() as session:
            yield session

    app.dependency_overrides[get_analytics_db] = _override_get_analytics_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
    app.dependency_overrides.clear()
