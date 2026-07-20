"""Unit tests for `app/services/session_service.py`."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.exceptions.base import NotFoundError
from app.services import session_service
from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_get_session_raises_not_found_for_an_unknown_id(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await session_service.get_session(session, uuid.uuid4())


async def test_get_session_returns_metadata(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        metadata = await session_service.get_session(session, seeded.bahrain_session_id)

    assert metadata.season == 2024
    assert metadata.session_type == "R"
    assert metadata.circuit == "Bahrain International Circuit"


async def test_get_results_raises_not_found_for_an_unknown_session(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await session_service.get_results(session, uuid.uuid4())


async def test_get_results_orders_by_finish_position(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        results = await session_service.get_results(session, seeded.bahrain_session_id)

    assert [entry.driver for entry in results] == ["Max Verstappen", "Charles Leclerc"]
    assert results[0].points == 25


async def test_get_laps_raises_not_found_for_an_unknown_session(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await session_service.get_laps(session, uuid.uuid4())


async def test_get_laps_returns_this_sessions_laps(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    async with analytics_session_factory() as session:
        laps = await session_service.get_laps(session, seeded.bahrain_session_id)

    assert len(laps) == 4
    assert laps[0].driver == "Max Verstappen"
