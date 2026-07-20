"""Unit tests for `app/repositories/race_repository.py`."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories import race_repository
from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_list_races_filters_by_season_and_country(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        rows, total = await race_repository.list_races(
            session, season=2024, country="Bahrain", page=1, limit=25
        )
        _, total_unmatched = await race_repository.list_races(
            session, season=1999, country=None, page=1, limit=25
        )

    assert total == 1
    assert rows[0].race_name == "Bahrain Grand Prix"
    assert total_unmatched == 0


async def test_get_race_by_id_returns_none_for_an_unknown_id(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        row = await race_repository.get_race_by_id(session, uuid.uuid4())

    assert row is None


async def test_race_exists_is_true_for_a_seeded_race_and_false_otherwise(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        exists = await race_repository.race_exists(session, seeded.bahrain_session_id)
        missing = await race_repository.race_exists(session, uuid.uuid4())

    assert exists is True
    assert missing is False


async def test_list_laps_for_strategy_orders_by_driver_then_lap_number(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    async with analytics_session_factory() as session:
        rows = await race_repository.list_laps_for_strategy(session, seeded.bahrain_session_id)

    assert [row.lap_number for row in rows] == [1, 2, 3, 4]
    assert rows[0].driver == "Max Verstappen"


async def test_list_pitstops_returns_only_this_sessions_stops(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    async with analytics_session_factory() as session:
        bahrain_stops = await race_repository.list_pitstops(session, seeded.bahrain_session_id)
        jeddah_stops = await race_repository.list_pitstops(session, seeded.jeddah_session_id)

    assert len(bahrain_stops) == 1
    assert bahrain_stops[0].driver == "Max Verstappen"
    assert jeddah_stops == []
