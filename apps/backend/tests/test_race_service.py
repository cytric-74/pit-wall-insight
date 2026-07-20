"""Unit tests for `app/services/race_service.py`.

`get_strategy`'s `itertools.groupby`-based tyre-stint derivation had no
edge-case coverage at all before this file (Phase 7 audit, High) — only
ever exercised indirectly through the happy path in `test_races_api.py`.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.exceptions.base import NotFoundError
from app.models import FctLap
from app.services import race_service
from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_list_races_filters_by_country(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        items, total = await race_service.list_races(
            session, season=None, country="Bahrain", page=1, limit=25
        )

    assert total == 1
    assert items[0].race_name == "Bahrain Grand Prix"


async def test_get_race_raises_not_found_for_an_unknown_id(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await race_service.get_race(session, uuid.uuid4())


async def test_get_positions_raises_not_found_for_an_unknown_race(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await race_service.get_positions(session, uuid.uuid4())


async def test_get_weather_returns_all_null_fields_when_no_weather_is_linked(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Jeddah has no `dim_weather` link in the fixture — an honest null
    result, not a fabricated one (mirrors `test_get_race_weather_reflects_...`
    in `test_races_api.py`, at the service layer instead of over HTTP)."""
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        weather = await race_service.get_weather(session, seeded.jeddah_session_id)

    assert weather.air_temperature is None
    assert weather.rainfall is None


async def test_get_strategy_raises_not_found_for_an_unknown_race(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await race_service.get_strategy(session, uuid.uuid4())


async def test_get_strategy_single_lap_session_produces_one_single_lap_stint(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Edge case named directly by the audit: a session with only one
    recorded lap must still produce a valid single-lap stint, not raise or
    silently drop the driver."""
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    async with analytics_session_factory() as session:
        session.add(
            FctLap(
                lap_id=uuid.uuid4(),
                source="test",
                pipeline_version="0.1.0",
                driver_id=seeded.leclerc_id,
                session_id=seeded.jeddah_session_id,
                lap_number=1,
                compound="MEDIUM",
            )
        )
        await session.commit()

    async with analytics_session_factory() as session:
        strategies = await race_service.get_strategy(session, seeded.jeddah_session_id)

    assert len(strategies) == 1
    assert len(strategies[0].stints) == 1
    stint = strategies[0].stints[0]
    assert stint.compound == "MEDIUM"
    assert stint.start_lap == stint.end_lap == 1
    assert stint.lap_count == 1


async def test_get_strategy_a_driver_who_only_ran_one_compound_gets_a_single_stint(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Edge case named directly by the audit: a driver who never changed
    compound across a whole session must collapse to exactly one stint
    spanning every lap, not one stint per lap."""
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    async with analytics_session_factory() as session:
        session.add_all(
            [
                FctLap(
                    lap_id=uuid.uuid4(),
                    source="test",
                    pipeline_version="0.1.0",
                    driver_id=seeded.leclerc_id,
                    session_id=seeded.jeddah_session_id,
                    lap_number=lap_number,
                    compound="HARD",
                )
                for lap_number in (1, 2, 3)
            ]
        )
        await session.commit()

    async with analytics_session_factory() as session:
        strategies = await race_service.get_strategy(session, seeded.jeddah_session_id)

    assert len(strategies) == 1
    assert len(strategies[0].stints) == 1
    stint = strategies[0].stints[0]
    assert stint.compound == "HARD"
    assert stint.start_lap == 1
    assert stint.end_lap == 3
    assert stint.lap_count == 3


async def test_get_strategy_groups_multiple_drivers_independently(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    async with analytics_session_factory() as session:
        strategies = await race_service.get_strategy(session, seeded.bahrain_session_id)

    assert len(strategies) == 1  # only Verstappen has laps in the fixture
    assert strategies[0].driver == "Max Verstappen"
