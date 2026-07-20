"""Integration tests for `/api/v1/sessions*`."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_get_session_returns_404_for_an_unknown_id(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/sessions/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_get_session_metadata(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get(f"/api/v1/sessions/{seeded.bahrain_session_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["season"] == 2024
    assert body["data"]["sessionType"] == "R"
    assert body["data"]["circuit"] == "Bahrain International Circuit"


async def test_get_session_results_ordered_by_finish_position(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get(f"/api/v1/sessions/{seeded.bahrain_session_id}/results")

    assert response.status_code == 200
    body = response.json()
    assert [entry["driver"] for entry in body["data"]] == ["Max Verstappen", "Charles Leclerc"]
    assert body["data"][0]["points"] == 25


async def test_get_session_laps(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    response = await client.get(f"/api/v1/sessions/{seeded.bahrain_session_id}/laps")

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 4
    assert body["data"][0]["driver"] == "Max Verstappen"
