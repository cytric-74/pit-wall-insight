"""Unit tests for `app/services/strategy_service.py`."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.exceptions.base import ValidationError
from app.services import strategy_service
from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_get_tyre_degradation_raises_validation_error_without_season_or_driver(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        with pytest.raises(ValidationError):
            await strategy_service.get_tyre_degradation(
                session, season=None, driver_id=None, round_number=None, session_type=None
            )


async def test_get_tyre_degradation_scoped_by_driver_groups_by_compound_and_tyre_life(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    async with analytics_session_factory() as session:
        degradation = await strategy_service.get_tyre_degradation(
            session,
            season=None,
            driver_id=seeded.verstappen_id,
            round_number=None,
            session_type=None,
        )

    # 4 seeded laps (SOFT tyreLife 1&2, HARD tyreLife 1&2) -- lap 2 is
    # pit_in=True and lap 3 is pit_out=True, both excluded, leaving 2 points.
    assert len(degradation.points) == 2
    assert degradation.points[0].compound == "HARD"
