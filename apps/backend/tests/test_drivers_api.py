"""Integration tests for `/api/v1/drivers*`."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tests.factories import (
    seed_2023_season_for_verstappen,
    seed_2024_two_race_season,
    seed_driver_and_constructor_stats,
)


async def test_list_drivers_supports_constructor_filter_and_pagination(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get(
        "/api/v1/drivers", params={"constructor": str(seeded.red_bull_id)}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["pagination"]["total"] == 1
    assert body["data"][0]["fullName"] == "Max Verstappen"
    assert body["data"][0]["teamId"] == str(seeded.red_bull_id)


async def test_get_driver_returns_404_for_an_unknown_id(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/drivers/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["success"] is False


async def test_get_driver_statistics_reflects_career_totals(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)
    await seed_2023_season_for_verstappen(analytics_session_factory, seeded.verstappen_id)

    response = await client.get(f"/api/v1/drivers/{seeded.verstappen_id}/statistics")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["seasonsCompeted"] == 2
    assert body["data"]["wins"] == 3


async def test_get_driver_laps_supports_compound_filter(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    response = await client.get(
        f"/api/v1/drivers/{seeded.verstappen_id}/laps", params={"compound": "SOFT"}
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    assert body["data"][0]["compound"] == "SOFT"


async def test_get_driver_consistency(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    response = await client.get(f"/api/v1/drivers/{seeded.verstappen_id}/consistency")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["careerConsistencyScore"] == 100.0


async def test_compare_drivers_returns_both_sides(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    response = await client.get(
        f"/api/v1/drivers/{seeded.verstappen_id}/comparison/{seeded.leclerc_id}"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["season"] == 2024
    assert body["data"]["driverA"]["driver"] == "Max Verstappen"
    assert body["data"]["driverB"]["driver"] == "Charles Leclerc"


async def test_compare_drivers_returns_404_when_no_common_season(
    client: AsyncClient, analytics_session_factory: async_sessionmaker[AsyncSession]
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    response = await client.get(
        f"/api/v1/drivers/{seeded.verstappen_id}/comparison/{seeded.leclerc_id}"
    )

    assert response.status_code == 404
