"""Unit tests for `app/repositories/driver_repository.py`."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories import driver_repository
from tests.factories import (
    seed_2023_season_for_verstappen,
    seed_2024_two_race_season,
    seed_driver_and_constructor_stats,
)


async def test_list_drivers_returns_both_drivers_sorted_by_full_name(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        rows, total = await driver_repository.list_drivers(
            session,
            season=None,
            constructor_id=None,
            nationality=None,
            active=None,
            sort="full_name",
            page=1,
            limit=25,
        )

    assert total == 2
    assert [row.full_name for row in rows] == ["Charles Leclerc", "Max Verstappen"]
    assert rows[0].team == "Ferrari"


async def test_list_drivers_filters_by_constructor(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        rows, total = await driver_repository.list_drivers(
            session,
            season=None,
            constructor_id=seeded.red_bull_id,
            nationality=None,
            active=None,
            sort="full_name",
            page=1,
            limit=25,
        )

    assert total == 1
    assert rows[0].full_name == "Max Verstappen"


async def test_list_drivers_filters_by_season(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        _, total_2024 = await driver_repository.list_drivers(
            session,
            season=2024,
            constructor_id=None,
            nationality=None,
            active=None,
            sort="full_name",
            page=1,
            limit=25,
        )
        _, total_1999 = await driver_repository.list_drivers(
            session,
            season=1999,
            constructor_id=None,
            nationality=None,
            active=None,
            sort="full_name",
            page=1,
            limit=25,
        )

    assert total_2024 == 2
    assert total_1999 == 0


async def test_get_driver_by_id_returns_none_for_an_unknown_id(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        row = await driver_repository.get_driver_by_id(session, uuid.uuid4())

    assert row is None


async def test_list_season_summaries_for_driver_spans_multiple_seasons(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)
    await seed_2023_season_for_verstappen(analytics_session_factory, seeded.verstappen_id)

    async with analytics_session_factory() as session:
        rows = await driver_repository.list_season_summaries_for_driver(
            session, seeded.verstappen_id
        )

    assert [row.season for row in rows] == [2023, 2024]
    assert rows[0].MartDriverSummary.wins == 1
    assert rows[1].MartDriverSummary.wins == 2


async def test_list_laps_for_driver_filters_by_compound(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    async with analytics_session_factory() as session:
        all_laps = await driver_repository.list_laps_for_driver(
            session,
            seeded.verstappen_id,
            season=None,
            round_number=None,
            session_type=None,
            compound=None,
        )
        soft_laps = await driver_repository.list_laps_for_driver(
            session,
            seeded.verstappen_id,
            season=None,
            round_number=None,
            session_type=None,
            compound="SOFT",
        )

    assert len(all_laps) == 2
    assert len(soft_laps) == 1
    assert soft_laps[0].compound == "SOFT"
    assert soft_laps[0].race_name == "Bahrain Grand Prix"
