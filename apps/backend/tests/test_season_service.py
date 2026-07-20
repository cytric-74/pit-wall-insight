"""Unit tests for `app/services/season_service.py` — the ranking/DTO-assembly
layer on top of `season_repository` (docs/05_BACKEND_ARCHITECTURE.md,
"Testing Strategy" -> "Unit Tests: Services").
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.exceptions.base import NotFoundError
from app.services import season_service
from tests.factories import seed_2024_two_race_season


async def test_get_ranked_driver_standings_assigns_position_by_points_order(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        standings = await season_service.get_ranked_driver_standings(session, seeded.season_id)

    assert [entry.position for entry in standings] == [1, 2]
    assert standings[0].driver == "Max Verstappen"
    assert standings[0].points == 50
    assert standings[1].driver == "Charles Leclerc"


async def test_get_season_summary_raises_not_found_for_an_unknown_year(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await season_service.get_season_summary(session, 1999)


async def test_get_season_summary_reflects_mart_dashboard_and_dim_season(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        summary = await season_service.get_season_summary(session, 2024)

    assert summary.year == 2024
    assert summary.champion_driver == "Max Verstappen"
    assert summary.fastest_lap_driver == "Max Verstappen"
    assert summary.championship_gap == 14.0


async def test_get_standings_returns_both_driver_and_constructor_lists(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        standings = await season_service.get_standings(session, 2024)

    assert standings.season == 2024
    assert len(standings.drivers) == 2
    assert len(standings.constructors) == 2
    assert standings.drivers[0].driver == "Max Verstappen"


async def test_get_calendar_returns_rounds_in_order(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        calendar = await season_service.get_calendar(session, 2024)

    assert [entry.race_name for entry in calendar] == [
        "Bahrain Grand Prix",
        "Saudi Arabian Grand Prix",
    ]


async def test_list_seasons_paginates(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        items, total = await season_service.list_seasons(session, page=1, limit=25)

    assert total == 1
    assert items[0].year == 2024
