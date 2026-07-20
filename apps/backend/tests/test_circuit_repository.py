"""Unit tests for `app/repositories/circuit_repository.py`."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories import circuit_repository
from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_list_circuits_paginates(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        rows, total = await circuit_repository.list_circuits(session, page=1, limit=25)

    assert total == 1
    assert rows[0].name == "Bahrain International Circuit"


async def test_get_circuit_by_id_returns_none_for_an_unknown_id(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        row = await circuit_repository.get_circuit_by_id(session, uuid.uuid4())

    assert row is None


async def test_list_race_history_orders_most_recent_season_first(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        rows = await circuit_repository.list_race_history(session, seeded.circuit_id)

    assert len(rows) == 1  # Jeddah has no circuit_id in the fixture
    assert rows[0].season == 2024
    assert rows[0].winner == "Max Verstappen"


async def test_get_track_record_returns_none_when_no_laps_are_recorded(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        row = await circuit_repository.get_track_record(session, seeded.circuit_id)

    assert row is None


async def test_get_track_record_returns_the_single_fastest_row(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    async with analytics_session_factory() as session:
        row = await circuit_repository.get_track_record(session, seeded.circuit_id)

    assert row is not None
    assert row.driver == "Max Verstappen"
    assert row.lap_time == 94.2
