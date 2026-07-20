"""Integration tests for `/api/v1/races*`."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_list_races_supports_season_filter(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get("/api/v1/races", params={"season": 2024})

    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] == 2
    assert body["data"][0]["raceName"] == "Saudi Arabian Grand Prix"  # round desc


async def test_get_race_returns_404_for_an_unknown_id(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/races/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_get_race_returns_the_summary(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get(f"/api/v1/races/{seeded.bahrain_session_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["raceName"] == "Bahrain Grand Prix"
    assert body["data"]["winner"] == "Max Verstappen"
    assert body["data"]["circuit"] == "Bahrain International Circuit"


async def test_get_race_positions(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    response = await client.get(f"/api/v1/races/{seeded.bahrain_session_id}/positions")

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 4
    assert body["data"][0]["driver"] == "Max Verstappen"


async def test_get_race_pitstops(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    response = await client.get(f"/api/v1/races/{seeded.bahrain_session_id}/pitstops")

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    assert body["data"][0]["pitDuration"] == 22.3
    assert body["data"][0]["compoundAfter"] == "HARD"


async def test_get_race_weather_reflects_the_linked_dim_weather_row(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    bahrain_response = await client.get(f"/api/v1/races/{seeded.bahrain_session_id}/weather")
    jeddah_response = await client.get(f"/api/v1/races/{seeded.jeddah_session_id}/weather")

    assert bahrain_response.json()["data"]["rainfall"] is False
    assert bahrain_response.json()["data"]["airTemperature"] == 24.0
    # Jeddah has no dim_weather link in the fixture -- honestly nulled, not fabricated.
    assert jeddah_response.json()["data"]["airTemperature"] is None


async def test_get_race_strategy_derives_stints_from_compound_changes(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    response = await client.get(f"/api/v1/races/{seeded.bahrain_session_id}/strategy")

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    stints = body["data"][0]["stints"]
    assert [stint["compound"] for stint in stints] == ["SOFT", "HARD"]
    assert stints[0]["lapCount"] == 2
    assert stints[1]["lapCount"] == 2
