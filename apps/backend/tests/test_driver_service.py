"""Unit tests for `app/services/driver_service.py`."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.exceptions.base import NotFoundError
from app.services import driver_service
from tests.factories import (
    seed_2023_season_for_verstappen,
    seed_2024_two_race_season,
    seed_driver_and_constructor_stats,
)


async def test_get_driver_raises_not_found_for_an_unknown_id(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await driver_service.get_driver(session, uuid.uuid4())


async def test_get_driver_returns_the_profile(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        driver = await driver_service.get_driver(session, seeded.verstappen_id)

    assert driver.full_name == "Max Verstappen"
    assert driver.team == "Red Bull Racing"


async def test_list_drivers_falls_back_to_default_sort_for_an_invalid_field(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        drivers, total = await driver_service.list_drivers(
            session,
            season=None,
            constructor_id=None,
            nationality=None,
            active=None,
            sort="not-a-real-field",
            page=1,
            limit=25,
        )

    assert total == 2
    assert [driver.full_name for driver in drivers] == ["Charles Leclerc", "Max Verstappen"]


async def test_get_career_statistics_sums_across_seasons(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)
    await seed_2023_season_for_verstappen(analytics_session_factory, seeded.verstappen_id)

    async with analytics_session_factory() as session:
        stats = await driver_service.get_career_statistics(session, seeded.verstappen_id)

    assert stats.seasons_competed == 2
    assert stats.wins == 3  # 1 (2023) + 2 (2024)
    assert stats.podiums == 3
    assert stats.average_finish == 1.0


async def test_get_career_statistics_handles_a_driver_with_no_mart_rows_yet(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        stats = await driver_service.get_career_statistics(session, seeded.verstappen_id)

    assert stats.seasons_competed == 0
    assert stats.wins == 0
    assert stats.average_finish is None


async def test_get_laps_raises_not_found_for_an_unknown_driver(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await driver_service.get_laps(
                session, uuid.uuid4(), season=None, round_number=None, session_type=None, compound=None
            )


async def test_get_laps_returns_lap_data_for_a_known_driver(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    async with analytics_session_factory() as session:
        laps = await driver_service.get_laps(
            session,
            seeded.verstappen_id,
            season=None,
            round_number=None,
            session_type=None,
            compound=None,
        )

    assert len(laps) == 2
    assert laps[0].lap_number == 1


async def test_get_consistency_averages_across_seasons(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)
    await seed_2023_season_for_verstappen(analytics_session_factory, seeded.verstappen_id)

    async with analytics_session_factory() as session:
        consistency = await driver_service.get_consistency(session, seeded.verstappen_id)

    assert consistency.driver == "Max Verstappen"
    assert len(consistency.seasons) == 2
    assert consistency.career_consistency_score == 100.0


async def test_compare_drivers_defaults_to_the_latest_common_season(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)
    await seed_2023_season_for_verstappen(analytics_session_factory, seeded.verstappen_id)

    async with analytics_session_factory() as session:
        comparison = await driver_service.compare_drivers(
            session, seeded.verstappen_id, seeded.leclerc_id, season=None
        )

    # Leclerc has no 2023 data, so the only common season is 2024.
    assert comparison.season == 2024
    assert comparison.driver_a.driver == "Max Verstappen"
    assert comparison.driver_b.driver == "Charles Leclerc"
    assert comparison.driver_a.wins == 2
    assert comparison.driver_b.wins == 0


async def test_compare_drivers_raises_not_found_when_no_season_is_shared(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_2023_season_for_verstappen(analytics_session_factory, seeded.verstappen_id)

    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await driver_service.compare_drivers(
                session, seeded.verstappen_id, seeded.leclerc_id, season=None
            )
