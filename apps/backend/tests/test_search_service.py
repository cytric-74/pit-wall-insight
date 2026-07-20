"""Unit tests for `app/services/search_service.py`."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.services import search_service
from tests.factories import seed_2024_two_race_season


async def test_search_matches_across_every_entity_type(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        results = await search_service.search(session, "bahrain")

    assert results.circuits[0].label == "Bahrain International Circuit"
    assert results.races[0].label == "Bahrain Grand Prix (2024)"
    assert results.drivers == []


async def test_search_returns_empty_lists_when_nothing_matches(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        results = await search_service.search(session, "no-such-entity-anywhere")

    assert results.drivers == []
    assert results.constructors == []
    assert results.circuits == []
    assert results.races == []
    assert results.seasons == []
