"""Smoke tests for `/health`, `/ready`, and `/live`."""

from __future__ import annotations

from httpx import AsyncClient


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
