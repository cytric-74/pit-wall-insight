"""Integration tests for the Gold-layer (`dim_*`/`fct_*`) SQLAlchemy models.

Same rationale as `tests/test_raw_models.py`: proves `app/models/gold/*.py`
produces a working schema — including the foreign keys *between* Gold
tables, which Bronze deliberately doesn't have (see
`app/models/raw/__init__.py`) — against a real (in-memory) SQLite
database, since this environment has no Docker/Postgres available.

SQLite enforces foreign keys only when `PRAGMA foreign_keys=ON` is set per
connection (off by default, for backward compatibility with pre-FK-support
SQLite databases) — this fixture turns it on via an engine-level event
listener, so the FK-violation test below actually exercises the same
constraint enforcement PostgreSQL provides natively.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from datetime import date

import pytest
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database.session import GoldBase
from app.models import (
    DimCircuit,
    DimConstructor,
    DimDriver,
    DimSeason,
    DimSession,
    DimWeather,
    FctLap,
    FctResult,
    MartConstructorSummary,
    MartDashboard,
    MartDriverSummary,
    MartRaceSummary,
)


@pytest.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    sync_engine = test_engine.sync_engine

    @event.listens_for(sync_engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection: object, _: object) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with test_engine.begin() as conn:
        await conn.run_sync(GoldBase.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False)


def _new_id() -> uuid.UUID:
    return uuid.uuid4()


async def test_dim_season_round_trips(session_factory: async_sessionmaker[AsyncSession]) -> None:
    season = DimSeason(
        season_id=_new_id(),
        source="transform",
        pipeline_version="0.1.0",
        year=2024,
        race_count=24,
        sprint_count=6,
        champion_driver="Max Verstappen",
        champion_constructor="Red Bull Racing",
    )
    async with session_factory() as session:
        session.add(season)
        await session.commit()

    async with session_factory() as session:
        fetched = await session.get(DimSeason, season.season_id)
        assert fetched is not None
        assert fetched.year == 2024
        assert fetched.champion_driver == "Max Verstappen"


async def test_dim_driver_foreign_key_to_dim_constructor(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    constructor_id = _new_id()
    async with session_factory() as session:
        session.add(
            DimConstructor(
                constructor_id=constructor_id,
                source="transform",
                pipeline_version="0.1.0",
                team_name="Red Bull Racing",
            )
        )
        await session.commit()

    driver_id = _new_id()
    async with session_factory() as session:
        session.add(
            DimDriver(
                driver_id=driver_id,
                source="transform",
                pipeline_version="0.1.0",
                full_name="Max Verstappen",
                abbreviation="VER",
                date_of_birth=date(1997, 9, 30),
                team_id=constructor_id,
            )
        )
        await session.commit()

    async with session_factory() as session:
        fetched = await session.get(DimDriver, driver_id)
        assert fetched is not None
        assert fetched.team_id == constructor_id
        assert fetched.date_of_birth == date(1997, 9, 30)


async def test_dim_driver_rejects_an_unknown_team_id(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        session.add(
            DimDriver(
                driver_id=_new_id(),
                source="transform",
                pipeline_version="0.1.0",
                full_name="Max Verstappen",
                team_id=uuid.uuid4(),  # no matching dim_constructor row
            )
        )
        with pytest.raises(IntegrityError):
            await session.commit()


async def test_dim_session_natural_key_uniqueness_is_enforced(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    season_id = _new_id()
    async with session_factory() as session:
        session.add(
            DimSeason(
                season_id=season_id,
                source="transform",
                pipeline_version="0.1.0",
                year=2024,
                race_count=24,
            )
        )
        await session.commit()

    common = {
        "source": "transform",
        "pipeline_version": "0.1.0",
        "season_id": season_id,
        "round_number": 1,
        "session_type": "R",
    }
    async with session_factory() as session:
        session.add(DimSession(session_id=_new_id(), **common))
        await session.commit()

    async with session_factory() as session:
        session.add(DimSession(session_id=_new_id(), **common))
        with pytest.raises(IntegrityError):
            await session.commit()


async def test_fct_results_and_fct_laps_reference_dim_session_and_dim_driver(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Exercises the full chain a real transform run produces: season -> session -> driver -> result/lap."""
    season_id = _new_id()
    driver_id = _new_id()
    session_id = _new_id()

    async with session_factory() as session:
        session.add(
            DimSeason(
                season_id=season_id,
                source="transform",
                pipeline_version="0.1.0",
                year=2024,
                race_count=24,
            )
        )
        session.add(
            DimDriver(
                driver_id=driver_id,
                source="transform",
                pipeline_version="0.1.0",
                full_name="Max Verstappen",
                abbreviation="VER",
            )
        )
        await session.commit()

    async with session_factory() as session:
        session.add(
            DimSession(
                session_id=session_id,
                source="transform",
                pipeline_version="0.1.0",
                season_id=season_id,
                round_number=1,
                session_type="R",
            )
        )
        await session.commit()

    async with session_factory() as session:
        session.add(
            FctResult(
                result_id=_new_id(),
                source="transform",
                pipeline_version="0.1.0",
                driver_id=driver_id,
                session_id=session_id,
                finish_position=1.0,
                points=25.0,
                fastest_lap=True,
                laps_completed=57,
            )
        )
        session.add(
            FctLap(
                lap_id=_new_id(),
                source="transform",
                pipeline_version="0.1.0",
                driver_id=driver_id,
                session_id=session_id,
                lap_number=1.0,
                lap_time=95.4,
            )
        )
        await session.commit()

    async with session_factory() as session:
        results = (
            await session.execute(FctResult.__table__.select().where(FctResult.session_id == session_id))
        ).mappings().all()
        assert len(results) == 1
        assert results[0]["points"] == 25.0


async def test_dim_circuit_and_dim_weather_round_trip(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    circuit = DimCircuit(
        circuit_id=_new_id(),
        source="transform",
        pipeline_version="0.1.0",
        name="Bahrain International Circuit",
        country="Bahrain",
        city="Sakhir",
        latitude=26.0325,
        longitude=50.5106,
    )
    weather = DimWeather(
        weather_id=_new_id(),
        source="transform",
        pipeline_version="0.1.0",
        air_temperature=24.5,
        track_temperature=31.2,
        rainfall=False,
    )
    async with session_factory() as session:
        session.add(circuit)
        session.add(weather)
        await session.commit()

    async with session_factory() as session:
        fetched_circuit = await session.get(DimCircuit, circuit.circuit_id)
        fetched_weather = await session.get(DimWeather, weather.weather_id)
        assert fetched_circuit is not None
        assert fetched_circuit.latitude == 26.0325
        assert fetched_weather is not None
        assert fetched_weather.rainfall is False


async def _seed_season_driver_and_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> tuple[uuid.UUID, uuid.UUID, uuid.UUID, uuid.UUID]:
    """Shared setup for the mart tests below: a season, a constructor, a
    driver on that constructor's team, and a race session — the minimum
    dimensional scaffolding every mart foreign-keys against. Returns
    (season_id, constructor_id, driver_id, session_id)."""
    season_id = _new_id()
    constructor_id = _new_id()
    driver_id = _new_id()
    session_id = _new_id()

    async with session_factory() as session:
        session.add(
            DimSeason(
                season_id=season_id,
                source="transform",
                pipeline_version="0.1.0",
                year=2024,
                race_count=24,
            )
        )
        session.add(
            DimConstructor(
                constructor_id=constructor_id,
                source="transform",
                pipeline_version="0.1.0",
                team_name="Red Bull Racing",
            )
        )
        await session.commit()

    async with session_factory() as session:
        session.add(
            DimDriver(
                driver_id=driver_id,
                source="transform",
                pipeline_version="0.1.0",
                full_name="Max Verstappen",
                abbreviation="VER",
                team_id=constructor_id,
            )
        )
        session.add(
            DimSession(
                session_id=session_id,
                source="transform",
                pipeline_version="0.1.0",
                season_id=season_id,
                round_number=1,
                session_type="R",
            )
        )
        await session.commit()

    return season_id, constructor_id, driver_id, session_id


async def test_mart_dashboard_round_trips_and_is_keyed_by_season(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    season_id, _constructor_id, _driver_id, _session_id = await _seed_season_driver_and_session(
        session_factory
    )

    async with session_factory() as session:
        session.add(
            MartDashboard(
                season_id=season_id,
                source="transform",
                pipeline_version="0.1.0",
                season=2024,
                drivers=20,
                constructors=10,
                races=24,
                fastest_pitstop=1.98,
                average_overtakes=12.5,
                fastest_lap_time=91.447,
                fastest_lap_driver="Max Verstappen",
                championship_gap=8.0,
            )
        )
        await session.commit()

    async with session_factory() as session:
        fetched = await session.get(MartDashboard, season_id)
        assert fetched is not None
        assert fetched.season == 2024
        assert fetched.fastest_lap_driver == "Max Verstappen"


async def test_mart_driver_summary_natural_key_uniqueness_is_enforced(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    season_id, _constructor_id, driver_id, _session_id = await _seed_season_driver_and_session(
        session_factory
    )

    common = {
        "source": "transform",
        "pipeline_version": "0.1.0",
        "season_id": season_id,
        "driver_id": driver_id,
        "driver": "Max Verstappen",
        "wins": 1,
        "podiums": 1,
        "poles": 0,
        "fastest_laps": 1,
    }
    async with session_factory() as session:
        session.add(MartDriverSummary(mart_driver_summary_id=_new_id(), **common))
        await session.commit()

    async with session_factory() as session:
        session.add(MartDriverSummary(mart_driver_summary_id=_new_id(), **common))
        with pytest.raises(IntegrityError):
            await session.commit()


async def test_mart_constructor_summary_round_trips(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    season_id, constructor_id, _driver_id, _session_id = await _seed_season_driver_and_session(
        session_factory
    )

    async with session_factory() as session:
        session.add(
            MartConstructorSummary(
                mart_constructor_summary_id=_new_id(),
                source="transform",
                pipeline_version="0.1.0",
                season_id=season_id,
                constructor_id=constructor_id,
                constructor="Red Bull Racing",
                wins=1,
                podiums=1,
                pitstop_average=2.3,
                average_points=25.0,
                dnf_rate=0.0,
            )
        )
        await session.commit()

    async with session_factory() as session:
        fetched = (
            await session.execute(
                MartConstructorSummary.__table__.select().where(
                    MartConstructorSummary.season_id == season_id
                )
            )
        ).mappings().one()
        assert fetched["constructor"] == "Red Bull Racing"
        assert fetched["strategy_success"] is None  # no source — see model docstring
        assert fetched["development_index"] is None


async def test_mart_race_summary_is_keyed_by_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    _season_id, _constructor_id, _driver_id, session_id = await _seed_season_driver_and_session(
        session_factory
    )

    async with session_factory() as session:
        session.add(
            MartRaceSummary(
                session_id=session_id,
                source="transform",
                pipeline_version="0.1.0",
                race="Bahrain Grand Prix",
                winner="Max Verstappen",
                fastest_lap="Max Verstappen",
                average_pitstop=2.3,
                weather="Dry",
                retirements=2,
            )
        )
        await session.commit()

    async with session_factory() as session:
        fetched = await session.get(MartRaceSummary, session_id)
        assert fetched is not None
        assert fetched.winner == "Max Verstappen"
        assert fetched.weather == "Dry"
        assert fetched.safety_car_laps is None  # no source — see model docstring
