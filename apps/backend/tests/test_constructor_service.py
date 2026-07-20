"""Unit tests for `app/services/constructor_service.py`."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.exceptions.base import NotFoundError
from app.services import constructor_service
from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_get_constructor_raises_not_found_for_an_unknown_id(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await constructor_service.get_constructor(session, uuid.uuid4())


async def test_get_current_drivers_attaches_the_constructor_name(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        drivers = await constructor_service.get_current_drivers(session, seeded.red_bull_id)

    assert len(drivers) == 1
    assert drivers[0].full_name == "Max Verstappen"
    assert drivers[0].team == "Red Bull Racing"


async def test_get_performance_trend_returns_one_entry_per_season(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    async with analytics_session_factory() as session:
        trend = await constructor_service.get_performance_trend(session, seeded.red_bull_id)

    assert len(trend) == 1
    assert trend[0].season == 2024
    assert trend[0].wins == 2


async def test_get_career_statistics_reflects_available_seasons(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    async with analytics_session_factory() as session:
        stats = await constructor_service.get_career_statistics(session, seeded.red_bull_id)

    assert stats.constructor == "Red Bull Racing"
    assert stats.seasons_competed == 1
    assert stats.wins == 2
    assert stats.average_points == 25.0
