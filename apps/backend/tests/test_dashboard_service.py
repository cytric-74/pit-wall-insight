"""Unit tests for `app/services/dashboard_service.py`."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.exceptions.base import NotFoundError
from app.models import DimSeason
from app.services import dashboard_service
from tests.factories import seed_2024_two_race_season


async def test_get_dashboard_raises_not_found_with_no_seasons_at_all(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await dashboard_service.get_dashboard(session)


async def test_get_dashboard_reflects_the_latest_season(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        data = await dashboard_service.get_dashboard(session)

    assert data.season == 2024
    assert data.champion_driver == "Max Verstappen"
    assert data.driver_standings[0].driver == "Max Verstappen"
    assert data.driver_standings[0].points == 50
    assert data.constructor_standings[0].constructor == "Red Bull Racing"
    assert [race.race_name for race in data.recent_races] == [
        "Saudi Arabian Grand Prix",
        "Bahrain Grand Prix",
    ]
    assert data.fastest_lap_driver == "Max Verstappen"
    assert data.championship_gap == 14.0


async def test_get_dashboard_highlights_reflects_the_most_recent_race(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        highlights = await dashboard_service.get_dashboard_highlights(session)

    assert highlights.race_name == "Saudi Arabian Grand Prix"
    assert highlights.winner == "Max Verstappen"
    assert highlights.pole == "Charles Leclerc"
    assert highlights.retirements == 2


async def test_get_dashboard_highlights_raises_not_found_when_no_race_has_been_completed(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """A season can exist (e.g. its calendar was ingested) before any race
    has actually been run/transformed — `mart_race_summary` stays empty
    until then, and highlights has nothing to report yet."""
    async with analytics_session_factory() as session:
        session.add(
            DimSeason(
                season_id=uuid.uuid4(),
                source="test",
                pipeline_version="0.1.0",
                year=2025,
                race_count=0,
                champion_driver=None,
                champion_constructor=None,
            )
        )
        await session.commit()

    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await dashboard_service.get_dashboard_highlights(session)
