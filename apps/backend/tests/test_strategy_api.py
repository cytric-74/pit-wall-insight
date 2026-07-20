"""Integration tests for `/api/v1/strategy/tyres`."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_tyre_degradation_groups_by_compound_and_tyre_life(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    response = await client.get(
        "/api/v1/strategy/tyres", params={"driver": str(seeded.verstappen_id)}
    )

    assert response.status_code == 200
    body = response.json()
    # 4 seeded laps (SOFT tyreLife 1&2, HARD tyreLife 1&2) -- lap 2 is
    # pit_in=True and lap 3 is pit_out=True, both excluded, leaving 2 points.
    assert len(body["data"]["points"]) == 2
    assert body["data"]["points"][0]["compound"] == "HARD"
    assert body["data"]["points"][0]["sampleCount"] == 1


async def test_tyre_degradation_returns_an_empty_list_when_nothing_matches(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get("/api/v1/strategy/tyres", params={"season": 1999})

    assert response.status_code == 200
    assert response.json()["data"]["points"] == []


async def test_tyre_degradation_requires_a_season_or_driver(client: AsyncClient) -> None:
    response = await client.get("/api/v1/strategy/tyres")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
