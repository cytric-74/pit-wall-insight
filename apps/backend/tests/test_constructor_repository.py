"""Unit tests for `app/repositories/constructor_repository.py`."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories import constructor_repository
from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_list_constructors_returns_both_sorted_by_team_name(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        models, total = await constructor_repository.list_constructors(session, page=1, limit=25)

    assert total == 2
    assert [model.team_name for model in models] == ["Ferrari", "Red Bull Racing"]


async def test_get_constructor_by_id_returns_none_for_an_unknown_id(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        model = await constructor_repository.get_constructor_by_id(session, uuid.uuid4())

    assert model is None


async def test_list_current_drivers_only_returns_active_drivers_for_that_team(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        drivers = await constructor_repository.list_current_drivers(session, seeded.red_bull_id)

    assert len(drivers) == 1
    assert drivers[0].full_name == "Max Verstappen"


async def test_list_season_summaries_for_constructor(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    async with analytics_session_factory() as session:
        rows = await constructor_repository.list_season_summaries_for_constructor(
            session, seeded.red_bull_id
        )

    assert len(rows) == 1
    assert rows[0].season == 2024
    assert rows[0].MartConstructorSummary.wins == 2
