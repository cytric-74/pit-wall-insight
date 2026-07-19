"""Integration tests for `loaders.bronze_loader`, against a real (temp-file) SQLite database.

Purpose
-------
`bronze_loader` reflects tables from a live database rather than importing
`apps/backend`'s ORM models (see that module's docstring for why). That
means these tests need *some* real database with the right tables already
present to reflect against — this file creates that schema itself, using
plain SQLAlchemy Core `Table` objects defined only here, deliberately
mirroring (but not importing) `apps/backend/app/models/raw/*.py`'s column
layout. This is the one place in `apps/ingestion` that duplicates schema
knowledge already expressed in `apps/backend` — an accepted, isolated
tradeoff of the "no cross-app import" architecture (see
`loaders/bronze_loader.py`'s module docstring), confined to test fixtures
rather than production loader code.

Why SQLite: no Docker/Postgres is available in this environment. Every
column type these tables use (`Uuid`, `String`, `Integer`, `Float`,
`Boolean`, `DateTime`) is portable across both dialects, and
`bronze_loader._upsert` explicitly supports both the `postgresql` and
`sqlite` dialects for exactly this reason — these tests exercise the same
`sqlite` code path production would use if it ever ran against SQLite, and
a structurally identical `postgresql` code path is exercised only by
inspection (there is no way to test the Postgres-specific branch without a
Postgres server).
"""

from __future__ import annotations

import uuid
from collections.abc import Generator

import pytest
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    Uuid,
    create_engine,
    func,
    select,
)
from sqlalchemy.engine import Engine

from loaders import bronze_loader
from validators.schema import (
    RawCircuitRef,
    RawConstructorRef,
    RawConstructorStanding,
    RawDriverRef,
    RawDriverStanding,
    RawEventSchedule,
    RawLocation,
    RawRaceCalendarEntry,
    RawRaceResult,
    RawSessionLap,
    RawSessionResult,
    RawWeatherSample,
)


def _audit_columns() -> list[Column]:  # type: ignore[type-arg]
    return [
        Column("id", Uuid(), primary_key=True),
        Column("source", String(), nullable=False),
        Column("pipeline_version", String(), nullable=False),
        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    ]


def _build_test_schema() -> MetaData:
    """Mirrors apps/backend/app/models/raw/*.py's table layout, for reflection-only testing."""
    metadata = MetaData()

    Table(
        "raw_circuits",
        metadata,
        *_audit_columns(),
        Column("circuit_id", String(), unique=True, nullable=False),
        Column("circuit_name", String(), nullable=False),
        Column("locality", String()),
        Column("country", String()),
        Column("latitude", String()),
        Column("longitude", String()),
    )
    Table(
        "raw_drivers",
        metadata,
        *_audit_columns(),
        Column("driver_id", String(), unique=True, nullable=False),
        Column("code", String()),
        Column("given_name", String(), nullable=False),
        Column("family_name", String(), nullable=False),
        Column("date_of_birth", String()),
        Column("nationality", String()),
    )
    Table(
        "raw_constructors",
        metadata,
        *_audit_columns(),
        Column("constructor_id", String(), unique=True, nullable=False),
        Column("name", String(), nullable=False),
        Column("nationality", String()),
    )
    Table(
        "raw_sessions",
        metadata,
        *_audit_columns(),
        Column("season", Integer(), nullable=False),
        Column("round_number", Integer(), nullable=False),
        Column("race_name", String()),
        Column("country", String()),
        Column("location", String()),
        Column("event_date", String()),
        Column("f1_api_support", Boolean()),
        UniqueConstraint("source", "season", "round_number"),
    )
    Table(
        "raw_results",
        metadata,
        *_audit_columns(),
        Column("season", Integer(), nullable=False),
        Column("round_number", Integer(), nullable=False),
        Column("session_type", String(), nullable=False),
        Column("driver_ref", String(), nullable=False),
        Column("position", Float()),
        Column("points", Float()),
        Column("status", String()),
        Column("grid_position", Float()),
        Column("driver_code", String()),
        Column("constructor_ref", String()),
        UniqueConstraint("source", "season", "round_number", "session_type", "driver_ref"),
    )
    Table(
        "raw_laps",
        metadata,
        *_audit_columns(),
        Column("season", Integer(), nullable=False),
        Column("round_number", Integer(), nullable=False),
        Column("session_type", String(), nullable=False),
        Column("driver_ref", String(), nullable=False),
        Column("lap_number", Float(), nullable=False),
        Column("lap_time", Float()),
        Column("sector_1_time", Float()),
        Column("sector_2_time", Float()),
        Column("sector_3_time", Float()),
        Column("compound", String()),
        Column("tyre_life", Float()),
        Column("stint", Float()),
        Column("pit_in_time", Float()),
        Column("pit_out_time", Float()),
        Column("position", Float()),
        UniqueConstraint(
            "source", "season", "round_number", "session_type", "driver_ref", "lap_number"
        ),
    )
    Table(
        "raw_weather",
        metadata,
        *_audit_columns(),
        Column("season", Integer(), nullable=False),
        Column("round_number", Integer(), nullable=False),
        Column("session_type", String(), nullable=False),
        Column("time_offset_seconds", Float(), nullable=False),
        Column("air_temp", Float()),
        Column("track_temp", Float()),
        Column("humidity", Float()),
        Column("pressure", Float()),
        Column("wind_direction", Float()),
        Column("wind_speed", Float()),
        Column("rainfall", Boolean()),
        UniqueConstraint("source", "season", "round_number", "session_type", "time_offset_seconds"),
    )
    return metadata


@pytest.fixture
def engine(tmp_path) -> Generator[Engine, None, None]:  # type: ignore[no-untyped-def]
    test_engine = create_engine(f"sqlite:///{tmp_path / 'bronze_test.db'}")
    _build_test_schema().create_all(test_engine)
    yield test_engine
    test_engine.dispose()


def _row_count(engine: Engine, table_name: str) -> int:
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)
    with engine.connect() as connection:
        result = connection.execute(select(func.count()).select_from(table))
        return int(result.scalar_one())


class TestReflectTableIdOverride:
    def test_id_round_trips_as_a_real_uuid_on_sqlite(self, engine: Engine) -> None:
        """The core premise `bronze_loader._reflect_table` exists to guarantee:
        without the explicit `Uuid()` override, SQLite would reflect `id` as a
        plain string/blob column, and a `uuid.UUID` value written through it
        would not read back as one."""
        table = bronze_loader._reflect_table(engine, "raw_circuits")
        row_id = uuid.uuid4()
        with engine.begin() as connection:
            connection.execute(
                table.insert().values(
                    id=row_id,
                    source="jolpica",
                    pipeline_version="0.1.0",
                    circuit_id="bahrain",
                    circuit_name="Bahrain International Circuit",
                )
            )
        with engine.connect() as connection:
            fetched = connection.execute(select(table.c.id)).scalar_one()
        assert fetched == row_id
        assert isinstance(fetched, uuid.UUID)


class TestUpsertCircuits:
    def test_inserts_distinct_circuits_and_deduplicates_within_a_batch(self, engine: Engine) -> None:
        entry = RawRaceCalendarEntry(
            season="2024",
            round="1",
            raceName="Bahrain Grand Prix",
            date="2024-03-02",
            Circuit=RawCircuitRef(
                circuitId="bahrain",
                circuitName="Bahrain International Circuit",
                Location=RawLocation(lat="26.0325", long="50.5106", locality="Sakhir", country="Bahrain"),
            ),
        )
        count = bronze_loader.upsert_circuits_from_calendar(
            engine, [entry, entry], pipeline_version="0.1.0"
        )

        assert count == 1  # deduplicated within the batch, by circuitId
        assert _row_count(engine, "raw_circuits") == 1

    def test_reingesting_the_same_circuit_updates_rather_than_duplicates(
        self, engine: Engine
    ) -> None:
        def make_entry(circuit_name: str) -> RawRaceCalendarEntry:
            return RawRaceCalendarEntry(
                season="2024",
                round="1",
                raceName="Bahrain Grand Prix",
                date="2024-03-02",
                Circuit=RawCircuitRef(
                    circuitId="bahrain",
                    circuitName=circuit_name,
                    Location=RawLocation(
                        lat="26.0325", long="50.5106", locality="Sakhir", country="Bahrain"
                    ),
                ),
            )

        bronze_loader.upsert_circuits_from_calendar(
            engine, [make_entry("Bahrain International Circuit")], pipeline_version="0.1.0"
        )
        bronze_loader.upsert_circuits_from_calendar(
            engine, [make_entry("Bahrain International Circuit (Renamed)")], pipeline_version="0.2.0"
        )

        assert _row_count(engine, "raw_circuits") == 1
        table = bronze_loader._reflect_table(engine, "raw_circuits")
        with engine.connect() as connection:
            row = connection.execute(select(table)).mappings().one()
        assert row["circuit_name"] == "Bahrain International Circuit (Renamed)"
        assert row["pipeline_version"] == "0.2.0"


class TestUpsertDriversAndConstructors:
    def test_upsert_drivers_deduplicates_by_driver_id(self, engine: Engine) -> None:
        driver = RawDriverRef(
            driverId="max_verstappen",
            code="VER",
            givenName="Max",
            familyName="Verstappen",
            dateOfBirth="1997-09-30",
            nationality="Dutch",
        )
        count = bronze_loader.upsert_drivers(engine, [driver, driver], pipeline_version="0.1.0")

        assert count == 1
        assert _row_count(engine, "raw_drivers") == 1

    def test_upsert_constructors_deduplicates_by_constructor_id(self, engine: Engine) -> None:
        constructor = RawConstructorRef(
            constructorId="red_bull", name="Red Bull Racing", nationality="Austrian"
        )
        count = bronze_loader.upsert_constructors(
            engine, [constructor, constructor], pipeline_version="0.1.0"
        )

        assert count == 1
        assert _row_count(engine, "raw_constructors") == 1


class TestUpsertSessions:
    def test_upsert_sessions_from_schedule_derives_season_from_event_date(
        self, engine: Engine
    ) -> None:
        event = RawEventSchedule(
            RoundNumber=1,
            EventName="Bahrain Grand Prix",
            Country="Bahrain",
            Location="Sakhir",
            EventDate="2024-03-02T00:00:00",
            F1ApiSupport=True,
        )
        count = bronze_loader.upsert_sessions_from_schedule(
            engine, [event], pipeline_version="0.1.0"
        )

        assert count == 1
        table = bronze_loader._reflect_table(engine, "raw_sessions")
        with engine.connect() as connection:
            row = connection.execute(select(table)).mappings().one()
        assert row["season"] == 2024
        assert row["source"] == "fastf1"
        assert row["f1_api_support"] is True

    def test_upsert_sessions_from_calendar_tags_source_as_jolpica(self, engine: Engine) -> None:
        entry = RawRaceCalendarEntry(
            season="2024",
            round="1",
            raceName="Bahrain Grand Prix",
            date="2024-03-02",
            Circuit=RawCircuitRef(
                circuitId="bahrain",
                circuitName="Bahrain International Circuit",
                Location=RawLocation(lat="26.0325", long="50.5106", locality="Sakhir", country="Bahrain"),
            ),
        )
        bronze_loader.upsert_sessions_from_calendar(engine, [entry], pipeline_version="0.1.0")

        table = bronze_loader._reflect_table(engine, "raw_sessions")
        with engine.connect() as connection:
            row = connection.execute(select(table)).mappings().one()
        assert row["source"] == "jolpica"
        assert row["season"] == 2024
        assert row["round_number"] == 1

    def test_fastf1_and_jolpica_rows_for_the_same_round_coexist(self, engine: Engine) -> None:
        """Bronze never merges across sources — both rows must survive."""
        event = RawEventSchedule(
            RoundNumber=1,
            EventName="Bahrain Grand Prix",
            Country="Bahrain",
            Location="Sakhir",
            EventDate="2024-03-02T00:00:00",
        )
        calendar_entry = RawRaceCalendarEntry(
            season="2024",
            round="1",
            raceName="Bahrain Grand Prix",
            date="2024-03-02",
            Circuit=RawCircuitRef(
                circuitId="bahrain",
                circuitName="Bahrain International Circuit",
                Location=RawLocation(lat="26.0325", long="50.5106", locality="Sakhir", country="Bahrain"),
            ),
        )
        bronze_loader.upsert_sessions_from_schedule(engine, [event], pipeline_version="0.1.0")
        bronze_loader.upsert_sessions_from_calendar(
            engine, [calendar_entry], pipeline_version="0.1.0"
        )

        assert _row_count(engine, "raw_sessions") == 2


class TestUpsertResults:
    def test_upsert_results_fastf1(self, engine: Engine) -> None:
        result = RawSessionResult(
            DriverNumber="1", Abbreviation="VER", TeamName="Red Bull", Position=1.0, Points=25.0
        )
        count = bronze_loader.upsert_results_fastf1(
            engine,
            [result],
            season=2024,
            round_number=1,
            session_type="R",
            pipeline_version="0.1.0",
        )

        assert count == 1
        table = bronze_loader._reflect_table(engine, "raw_results")
        with engine.connect() as connection:
            row = connection.execute(select(table)).mappings().one()
        assert row["driver_ref"] == "1"
        assert row["session_type"] == "R"
        assert row["source"] == "fastf1"
        assert row["driver_code"] == "VER"
        assert row["constructor_ref"] == "Red Bull"

    def test_upsert_results_jolpica_always_uses_session_type_r(self, engine: Engine) -> None:
        result = RawRaceResult(
            number="1",
            position="1",
            positionText="1",
            points="25",
            grid="1",
            laps="57",
            status="Finished",
            Driver=RawDriverRef(
                driverId="max_verstappen",
                code="VER",
                givenName="Max",
                familyName="Verstappen",
                dateOfBirth="1997-09-30",
                nationality="Dutch",
            ),
            Constructor=RawConstructorRef(
                constructorId="red_bull", name="Red Bull Racing", nationality="Austrian"
            ),
        )
        count = bronze_loader.upsert_results_jolpica(
            engine, [result], season=2024, round_number=1, pipeline_version="0.1.0"
        )

        assert count == 1
        table = bronze_loader._reflect_table(engine, "raw_results")
        with engine.connect() as connection:
            row = connection.execute(select(table)).mappings().one()
        assert row["driver_ref"] == "max_verstappen"
        assert row["session_type"] == "R"
        assert row["source"] == "jolpica"
        assert row["driver_code"] is None
        assert row["constructor_ref"] == "red_bull"


class TestUpsertLapsAndWeather:
    def test_upsert_laps_preserves_pit_stop_columns(self, engine: Engine) -> None:
        lap = RawSessionLap(
            Driver="VER",
            LapNumber=18.0,
            LapTime=95.4,
            Compound="HARD",
            PitInTime=1024.5,
            PitOutTime=1048.2,
        )
        count = bronze_loader.upsert_laps(
            engine,
            [lap],
            season=2024,
            round_number=1,
            session_type="R",
            pipeline_version="0.1.0",
        )

        assert count == 1
        table = bronze_loader._reflect_table(engine, "raw_laps")
        with engine.connect() as connection:
            row = connection.execute(select(table)).mappings().one()
        assert row["pit_in_time"] == 1024.5
        assert row["pit_out_time"] == 1048.2

    def test_upsert_weather(self, engine: Engine) -> None:
        sample = RawWeatherSample(
            Time=120.0,
            AirTemp=24.5,
            TrackTemp=31.2,
            Humidity=45.0,
            Pressure=1008.5,
            Rainfall=False,
            WindDirection=180.0,
            WindSpeed=1.5,
        )
        count = bronze_loader.upsert_weather(
            engine,
            [sample],
            season=2024,
            round_number=1,
            session_type="R",
            pipeline_version="0.1.0",
        )

        assert count == 1
        table = bronze_loader._reflect_table(engine, "raw_weather")
        with engine.connect() as connection:
            row = connection.execute(select(table)).mappings().one()
        assert row["time_offset_seconds"] == 120.0
        assert row["rainfall"] is False


def test_upsert_returns_zero_for_an_empty_batch(engine: Engine) -> None:
    count = bronze_loader.upsert_circuits_from_calendar(engine, [], pipeline_version="0.1.0")
    assert count == 0
    assert _row_count(engine, "raw_circuits") == 0


def test_driver_standings_and_constructor_standings_extraction(engine: Engine) -> None:
    """Exercises the nested-ref extraction paths main.py relies on for the
    two standings entities, which each contribute to two different
    tables."""
    standing = RawDriverStanding(
        position="1",
        points="575",
        wins="19",
        Driver=RawDriverRef(
            driverId="max_verstappen",
            code="VER",
            givenName="Max",
            familyName="Verstappen",
            dateOfBirth="1997-09-30",
            nationality="Dutch",
        ),
        Constructors=[
            RawConstructorRef(constructorId="red_bull", name="Red Bull Racing", nationality="Austrian")
        ],
    )
    driver_count = bronze_loader.upsert_drivers(
        engine, [standing.Driver], pipeline_version="0.1.0"
    )
    constructor_count = bronze_loader.upsert_constructors(
        engine, standing.Constructors, pipeline_version="0.1.0"
    )

    assert driver_count == 1
    assert constructor_count == 1
    assert _row_count(engine, "raw_drivers") == 1
    assert _row_count(engine, "raw_constructors") == 1


def test_constructor_standing_extraction(engine: Engine) -> None:
    standing = RawConstructorStanding(
        position="1",
        points="860",
        wins="21",
        Constructor=RawConstructorRef(
            constructorId="red_bull", name="Red Bull Racing", nationality="Austrian"
        ),
    )
    count = bronze_loader.upsert_constructors(
        engine, [standing.Constructor], pipeline_version="0.1.0"
    )
    assert count == 1
