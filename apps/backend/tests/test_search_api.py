"""Integration tests for `/api/v1/search`."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tests.factories import seed_2024_two_race_season


async def test_search_matches_drivers_case_insensitively(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get("/api/v1/search", params={"query": "verstap"})

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["drivers"][0]["label"] == "Max Verstappen"
    assert body["data"]["constructors"] == []


async def test_search_matches_across_every_entity_type(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get("/api/v1/search", params={"query": "bahrain"})

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["circuits"][0]["label"] == "Bahrain International Circuit"
    assert body["data"]["races"][0]["label"] == "Bahrain Grand Prix (2024)"


async def test_search_matches_seasons_by_year_substring(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get("/api/v1/search", params={"query": "2024"})

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["seasons"][0]["label"] == "2024"


async def test_search_requires_a_non_empty_query(client: AsyncClient) -> None:
    response = await client.get("/api/v1/search", params={"query": ""})

    assert response.status_code == 422
