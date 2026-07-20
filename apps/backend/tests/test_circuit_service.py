"""Unit tests for `app/services/circuit_service.py`."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.exceptions.base import NotFoundError
from app.services import circuit_service
from tests.factories import seed_2024_two_race_season, seed_driver_and_constructor_stats


async def test_get_circuit_raises_not_found_for_an_unknown_id(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await circuit_service.get_circuit(session, uuid.uuid4())


async def test_get_circuit_returns_the_profile(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        circuit = await circuit_service.get_circuit(session, seeded.circuit_id)

    assert circuit.name == "Bahrain International Circuit"
    assert circuit.country == "Bahrain"


async def test_list_circuits_returns_a_paginated_page(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        circuits, total = await circuit_service.list_circuits(session, page=1, limit=25)

    assert total == 1
    assert circuits[0].name == "Bahrain International Circuit"


async def test_get_race_history_raises_not_found_for_an_unknown_circuit(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with analytics_session_factory() as session:
        with pytest.raises(NotFoundError):
            await circuit_service.get_race_history(session, uuid.uuid4())


async def test_get_race_history_returns_only_races_at_that_circuit(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Jeddah has no `circuit_id` in the fixture, so only Bahrain should
    show up in this circuit's history — mirrors the API-level assertion in
    `test_circuits_api.py`, one layer down."""
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        history = await circuit_service.get_race_history(session, seeded.circuit_id)

    assert len(history) == 1
    assert history[0].race_name == "Bahrain Grand Prix"
    assert history[0].winner == "Max Verstappen"


async def test_get_track_record_returns_all_null_fields_when_no_laps_are_recorded(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Before any `fct_laps` row exists for a circuit, the record must be
    an honest null result, not a fabricated zero/empty string."""
    seeded = await seed_2024_two_race_season(analytics_session_factory)

    async with analytics_session_factory() as session:
        record = await circuit_service.get_track_record(session, seeded.circuit_id)

    assert record.driver is None
    assert record.lap_time is None


async def test_get_track_record_returns_the_fastest_lap_ever_recorded(
    analytics_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    seeded = await seed_2024_two_race_season(analytics_session_factory)
    await seed_driver_and_constructor_stats(analytics_session_factory, seeded)

    async with analytics_session_factory() as session:
        record = await circuit_service.get_track_record(session, seeded.circuit_id)

    assert record.driver == "Max Verstappen"
    assert record.lap_time == 94.2
