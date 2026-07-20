"""Unit tests for `app/repositories/strategy_repository.py`."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories import strategy_repository
from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_get_tyre_degradation_excludes_pit_in_and_pit_out_laps(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """In-lap/out-lap laps reflect entering/exiting the pits, not tyre
    performance — the fixture's lap 2 (pit_in=True) and lap 3 (pit_out=True)
    must both be excluded, leaving only laps 1 and 4."""
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    async with analytics_session_factory() as session:
        rows = await strategy_repository.get_tyre_degradation(
            session, season=None, driver_id=seeded.verstappen_id, round_number=None, session_type=None
        )

    assert len(rows) == 2
    assert {row.compound for row in rows} == {"SOFT", "HARD"}


async def test_get_tyre_degradation_filters_by_season(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    async with analytics_session_factory() as session:
        matched = await strategy_repository.get_tyre_degradation(
            session, season=2024, driver_id=None, round_number=None, session_type=None
        )
        unmatched = await strategy_repository.get_tyre_degradation(
            session, season=1999, driver_id=None, round_number=None, session_type=None
        )

    assert len(matched) == 2
    assert unmatched == []
