"""Unit tests for `app/repositories/season_repository.py` (docs/05_BACKEND_ARCHITECTURE.md,
"Testing Strategy" -> "Unit Tests: Repositories").

Exercises the raw queries directly against the seeded in-memory database
(`tests/factories.py`), independent of any service-layer ranking/DTO logic.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories import season_repository
from tests.factories import seed_2024_two_race_season


async def test_get_latest_season_returns_the_highest_year(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        season = await season_repository.get_latest_season(session)

    assert season is not None
    assert season.season_id == seeded.season_id
    assert season.year == 2024


async def test_get_latest_season_returns_none_when_no_seasons_exist(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        season = await season_repository.get_latest_season(session)

    assert season is None


async def test_get_driver_standings_orders_by_points_descending(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        rows = await season_repository.get_driver_standings(session, seeded.season_id)

    assert [row.driver for row in rows] == ["Max Verstappen", "Charles Leclerc"]
    assert rows[0].points == 50
    assert rows[0].wins == 2
    assert rows[0].team == "Red Bull Racing"
    assert rows[1].points == 36
    assert rows[1].wins == 0


async def test_get_constructor_standings_sums_across_drivers(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        rows = await season_repository.get_constructor_standings(session, seeded.season_id)

    assert [row.constructor for row in rows] == ["Red Bull Racing", "Ferrari"]
    assert rows[0].points == 50
    assert rows[1].points == 36


async def test_get_calendar_orders_by_round_and_attaches_circuit(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        rows = await season_repository.get_calendar(session, seeded.season_id)

    assert [row.race_name for row in rows] == ["Bahrain Grand Prix", "Saudi Arabian Grand Prix"]
    assert rows[0].circuit == "Bahrain International Circuit"
    assert rows[1].circuit is None  # no circuit linked for this session in the fixture


async def test_list_recent_completed_races_orders_by_round_descending(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        rows = await season_repository.list_recent_completed_races(
            session, seeded.season_id, limit=1
        )

    assert len(rows) == 1
    assert rows[0].race_name == "Saudi Arabian Grand Prix"
    assert rows[0].winner == "Max Verstappen"
    assert rows[0].retirements == 2
