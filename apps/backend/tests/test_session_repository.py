"""Unit tests for `app/repositories/session_repository.py`."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories import session_repository
from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_get_session_by_id_returns_none_for_an_unknown_id(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        row = await session_repository.get_session_by_id(session, uuid.uuid4())

    assert row is None


async def test_session_exists_is_true_for_a_seeded_session_and_false_otherwise(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        exists = await session_repository.session_exists(session, seeded.bahrain_session_id)
        missing = await session_repository.session_exists(session, uuid.uuid4())

    assert exists is True
    assert missing is False


async def test_list_results_orders_by_finish_position(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        rows = await session_repository.list_results(session, seeded.bahrain_session_id)

    assert [row.driver for row in rows] == ["Max Verstappen", "Charles Leclerc"]
    assert rows[0].team == "Red Bull Racing"


async def test_list_laps_orders_by_driver_then_lap_number(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    async with analytics_session_factory() as session:
        rows = await session_repository.list_laps(session, seeded.bahrain_session_id)

    assert [row.lap_number for row in rows] == [1, 2, 3, 4]
    assert rows[0].compound == "SOFT"
