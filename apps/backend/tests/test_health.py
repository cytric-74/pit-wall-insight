"""Smoke tests for `/health`, `/ready`, and `/live`."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from httpx import AsyncClient

from app.dependencies.database import get_analytics_db
from app.main import app


async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["environment"] == "development"
    assert body["version"] == "v1"
    assert "X-Request-ID" in response.headers


async def test_ready_returns_ready_when_the_analytics_database_is_reachable(
    client: AsyncClient,
) -> None:
    response = await client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


async def test_live_always_returns_alive(client: AsyncClient) -> None:
    response = await client.get("/live")

    assert response.status_code == 200
    assert response.json()["status"] == "alive"


async def test_ready_returns_503_when_the_analytics_database_is_unreachable(
    client: AsyncClient,
) -> None:
    """`/ready`'s explicit 503-on-DB-failure branch (`app/api/health.py`) is
    the single piece of logic in the codebase purpose-built for a database
    outage; before this test it was only ever exercised on its happy path
    (Phase 7 audit, Medium)."""

    class _BrokenSession:
        async def execute(self, *args: object, **kwargs: object) -> None:
            raise ConnectionError("simulated database outage")

    async def _override_get_analytics_db() -> AsyncGenerator[_BrokenSession, None]:
        yield _BrokenSession()

    app.dependency_overrides[get_analytics_db] = _override_get_analytics_db
    try:
        response = await client.get("/ready")
    finally:
        del app.dependency_overrides[get_analytics_db]

    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "NOT_READY"
