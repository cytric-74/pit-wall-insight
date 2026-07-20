"""Integration tests for `/api/v1/constructors*`."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_list_constructors_returns_a_collection_response(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get("/api/v1/constructors")

    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] == 2
    assert [item["teamName"] for item in body["data"]] == ["Ferrari", "Red Bull Racing"]


async def test_get_constructor_returns_404_for_an_unknown_id(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/constructors/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_get_constructor_drivers_returns_the_current_roster(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get(f"/api/v1/constructors/{seeded.red_bull_id}/drivers")

    assert response.status_code == 200
    body = response.json()
    assert body["data"][0]["fullName"] == "Max Verstappen"


async def test_get_constructor_statistics(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    response = await client.get(f"/api/v1/constructors/{seeded.red_bull_id}/statistics")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["wins"] == 2
    assert body["data"]["averagePoints"] == 25.0


async def test_get_constructor_performance_trend(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    response = await client.get(f"/api/v1/constructors/{seeded.red_bull_id}/performance")

    assert response.status_code == 200
    body = response.json()
    assert body["data"][0]["season"] == 2024
