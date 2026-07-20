"""Unit tests for `app/repositories/search_repository.py`."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories import search_repository
from tests.factories import seed_2024_two_race_season


async def test_search_drivers_matches_case_insensitively(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        results = await search_repository.search_drivers(session, "VERSTAP")

    assert [driver.full_name for driver in results] == ["Max Verstappen"]


async def test_search_constructors_matches_a_substring(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        results = await search_repository.search_constructors(session, "ferrari")

    assert [constructor.team_name for constructor in results] == ["Ferrari"]


async def test_search_circuits_matches_a_substring(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        results = await search_repository.search_circuits(session, "bahrain")

    assert results[0].name == "Bahrain International Circuit"


async def test_search_races_only_matches_race_sessions(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        results = await search_repository.search_races(session, "grand prix")

    assert len(results) == 2
    assert {row.race_name for row in results} == {
        "Bahrain Grand Prix",
        "Saudi Arabian Grand Prix",
    }


async def test_search_seasons_matches_by_year_substring(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        matches = await search_repository.search_seasons(session, "2024")
        misses = await search_repository.search_seasons(session, "1999")

    assert [row.year for row in matches] == [2024]
    assert misses == []


async def test_search_drivers_respects_the_limit_parameter(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        results = await search_repository.search_drivers(session, "a", limit=1)

    assert len(results) == 1
