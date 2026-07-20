"""Integration tests for `/api/v1/compare/*`."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_compare_drivers(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    response = await client.get(
        "/api/v1/compare/drivers",
        params={"driverA": str(seeded.verstappen_id), "driverB": str(seeded.leclerc_id)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["driverA"]["driver"] == "Max Verstappen"
    assert body["data"]["driverB"]["driver"] == "Charles Leclerc"


async def test_compare_constructors(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    response = await client.get(
        "/api/v1/compare/constructors",
        params={"constructorA": str(seeded.red_bull_id), "constructorB": str(seeded.ferrari_id)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["constructorA"]["constructor"] == "Red Bull Racing"
    assert body["data"]["constructorB"]["constructor"] == "Ferrari"


async def test_compare_races(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get(
        "/api/v1/compare/races",
        params={"raceA": str(seeded.bahrain_session_id), "raceB": str(seeded.jeddah_session_id)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["raceA"]["raceName"] == "Bahrain Grand Prix"
    assert body["data"]["raceB"]["raceName"] == "Saudi Arabian Grand Prix"
