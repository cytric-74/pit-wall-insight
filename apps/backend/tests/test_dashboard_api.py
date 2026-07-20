"""Integration tests for `/api/v1/dashboard*` — through the real FastAPI app,
proving the router -> service -> repository -> response-envelope path works
end to end (docs/05_BACKEND_ARCHITECTURE.md, "Testing Strategy" -> "Integration
Tests: API Routes").
"""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tests.factories import seed_2024_two_race_season


async def test_dashboard_returns_success_envelope_with_camel_case_data(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get("/api/v1/dashboard")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["season"] == 2024
    assert body["data"]["championDriver"] == "Max Verstappen"
    assert body["data"]["driverStandings"][0]["driver"] == "Max Verstappen"
    assert body["data"]["driverStandings"][0]["points"] == 50
    assert body["data"]["constructorStandings"][0]["constructor"] == "Red Bull Racing"
    assert body["data"]["recentRaces"][0]["raceName"] == "Saudi Arabian Grand Prix"
    assert body["data"]["championshipGap"] == 14.0
    assert "requestId" in body["meta"]
    assert "executionTime" in body["meta"]


async def test_dashboard_returns_404_with_error_envelope_when_no_data_exists(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/v1/dashboard")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "NOT_FOUND"


async def test_dashboard_highlights_reflects_the_most_recent_race(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get("/api/v1/dashboard/highlights")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["raceName"] == "Saudi Arabian Grand Prix"
    assert body["data"]["winner"] == "Max Verstappen"
