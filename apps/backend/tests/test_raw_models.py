"""Integration tests for the Bronze-layer (`raw_*`) SQLAlchemy models.

Purpose
-------
Proves `app/models/raw/*.py` actually produces a working schema and that
rows can be written and read back through it — not just that the Python
class definitions import without error. Runs against a real (in-memory)
SQLite database via `aiosqlite`, since this environment has no
Docker/Postgres available; every column type used in these models
(`Uuid`, `String`, `Integer`, `Float`, `Boolean`, `DateTime(timezone=True)`)
is portable across both SQLite and PostgreSQL, so this is genuine
integration coverage of the same model definitions that will run against
Postgres in production — not a separate, parallel implementation being
tested instead.

This file deliberately does not use the async engine wired up in
`app/database/session.py` (which is hardcoded to the Postgres/asyncpg URL
from `Settings`) — each test builds its own throwaway SQLite engine, so
these tests never depend on `DATABASE_URL` being set to anything in
particular, and never touch a real database.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database.session import Base
from app.models import (
    RawCircuit,
    RawConstructor,
    RawDriver,
    RawLap,
    RawResult,
    RawSession,
    RawWeather,
)


@pytest.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """A fresh, empty in-memory SQLite database with every raw_* table created."""
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False)


def _new_id() -> uuid.UUID:
    return uuid.uuid4()


async def test_raw_circuit_round_trips(session_factory: async_sessionmaker[AsyncSession]) -> None:
    circuit = RawCircuit(
        id=_new_id(),
        source="jolpica",
        pipeline_version="0.1.0",
        circuit_id="bahrain",
        circuit_name="Bahrain International Circuit",
        locality="Sakhir",
        country="Bahrain",
        latitude="26.0325",
        longitude="50.5106",
    )
    async with session_factory() as session:
        session.add(circuit)
        await session.commit()

    async with session_factory() as session:
        fetched = await session.get(RawCircuit, circuit.id)
        assert fetched is not None
        assert fetched.circuit_id == "bahrain"
        assert fetched.circuit_name == "Bahrain International Circuit"
        # created_at/updated_at come from the column's server_default —
        # asserting they're populated confirms AuditMixin's defaults fire
        # correctly against a real database, not just that the attribute
        # exists on the Python class.
        assert fetched.created_at is not None
        assert fetched.updated_at is not None


async def test_raw_driver_nullable_code_is_allowed(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Pre-2014 drivers have no Jolpica `code` — must be storable as NULL."""
    driver = RawDriver(
        id=_new_id(),
        source="jolpica",
        pipeline_version="0.1.0",
        driver_id="fangio",
        code=None,
        given_name="Juan Manuel",
        family_name="Fangio",
        date_of_birth="1911-06-24",
        nationality="Argentine",
    )
    async with session_factory() as session:
        session.add(driver)
        await session.commit()

    async with session_factory() as session:
        fetched = await session.get(RawDriver, driver.id)
        assert fetched is not None
        assert fetched.code is None


async def test_raw_constructor_round_trips(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    constructor = RawConstructor(
        id=_new_id(),
        source="jolpica",
        pipeline_version="0.1.0",
        constructor_id="red_bull",
        name="Red Bull Racing",
        nationality="Austrian",
    )
    async with session_factory() as session:
        session.add(constructor)
        await session.commit()

    async with session_factory() as session:
        fetched = await session.get(RawConstructor, constructor.id)
        assert fetched is not None
        assert fetched.name == "Red Bull Racing"


async def test_raw_session_natural_key_uniqueness_is_enforced(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """(source, season, round_number) must be unique — inserting a second
    row for the same key should be rejected by the database, not silently
    accepted as a duplicate."""
    common = {
        "source": "fastf1",
        "pipeline_version": "0.1.0",
        "season": 2024,
        "round_number": 1,
        "race_name": "Bahrain Grand Prix",
    }
    async with session_factory() as session:
        session.add(RawSession(id=_new_id(), **common))
        await session.commit()

    async with session_factory() as session:
        session.add(RawSession(id=_new_id(), **common))
        with pytest.raises(IntegrityError):
            await session.commit()


async def test_raw_result_round_trips(session_factory: async_sessionmaker[AsyncSession]) -> None:
    result = RawResult(
        id=_new_id(),
        source="fastf1",
        pipeline_version="0.1.0",
        season=2024,
        round_number=1,
        session_type="R",
        driver_ref="1",
        position=1.0,
        points=25.0,
        status="Finished",
        grid_position=1.0,
    )
    async with session_factory() as session:
        session.add(result)
        await session.commit()

    async with session_factory() as session:
        fetched = await session.get(RawResult, result.id)
        assert fetched is not None
        assert fetched.points == 25.0


async def test_raw_lap_round_trips_with_pit_stop_columns(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    lap = RawLap(
        id=_new_id(),
        source="fastf1",
        pipeline_version="0.1.0",
        season=2024,
        round_number=1,
        session_type="R",
        driver_ref="VER",
        lap_number=18.0,
        lap_time=95.4,
        sector_1_time=30.1,
        sector_2_time=35.2,
        sector_3_time=30.1,
        compound="HARD",
        tyre_life=1.0,
        stint=2.0,
        pit_in_time=None,
        pit_out_time=None,
        position=1.0,
    )
    async with session_factory() as session:
        session.add(lap)
        await session.commit()

    async with session_factory() as session:
        fetched = await session.get(RawLap, lap.id)
        assert fetched is not None
        assert fetched.compound == "HARD"
        assert fetched.pit_in_time is None


async def test_raw_weather_round_trips(session_factory: async_sessionmaker[AsyncSession]) -> None:
    weather = RawWeather(
        id=_new_id(),
        source="fastf1",
        pipeline_version="0.1.0",
        season=2024,
        round_number=1,
        session_type="R",
        time_offset_seconds=120.0,
        air_temp=24.5,
        track_temp=31.2,
        humidity=45.0,
        pressure=1008.5,
        wind_direction=180.0,
        wind_speed=1.5,
        rainfall=False,
    )
    async with session_factory() as session:
        session.add(weather)
        await session.commit()

    async with session_factory() as session:
        fetched = await session.get(RawWeather, weather.id)
        assert fetched is not None
        assert fetched.rainfall is False


async def test_deterministic_id_upsert_pattern_works(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Simulates the exact idempotent-reingestion pattern
    `apps/ingestion`'s loaders rely on: the same deterministic id, inserted
    twice, should update the existing row rather than create a duplicate.
    This is a merge/upsert at the ORM level (`Session.merge`), standing in
    for the dialect-specific `INSERT ... ON CONFLICT` SQL the real loader
    issues (see `apps/ingestion/loaders/bronze_loader.py`) — what matters
    here is confirming the model's primary key is the right thing to
    upsert on, not the exact SQL dialect used to do it.
    """
    fixed_id = uuid.uuid5(uuid.NAMESPACE_DNS, "test:circuit:bahrain")

    async with session_factory() as session:
        await session.merge(
            RawCircuit(
                id=fixed_id,
                source="jolpica",
                pipeline_version="0.1.0",
                circuit_id="bahrain",
                circuit_name="Bahrain International Circuit",
            )
        )
        await session.commit()

    async with session_factory() as session:
        await session.merge(
            RawCircuit(
                id=fixed_id,
                source="jolpica",
                pipeline_version="0.2.0",
                circuit_id="bahrain",
                circuit_name="Bahrain International Circuit (renamed)",
            )
        )
        await session.commit()

    async with session_factory() as session:
        fetched = await session.get(RawCircuit, fixed_id)
        assert fetched is not None
        assert fetched.circuit_name == "Bahrain International Circuit (renamed)"
        assert fetched.pipeline_version == "0.2.0"
