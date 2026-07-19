"""Integration tests for `transformers.bronze_to_gold.run_transform`.

Purpose
-------
Exercises the full Bronze -> Gold pipeline end to end against two real
(temp-file) SQLite databases — one standing in for the raw/bronze
database, one for the analytics/gold database, since this environment has
no Docker/Postgres available. Raw data is seeded via `loaders.bronze_loader`
(the same functions a real `collect` run would call), not hand-inserted
SQL, so these tests exercise the same collect-then-transform path
production actually takes.

The schemas built here (`_build_raw_schema`/`_build_gold_schema`)
deliberately duplicate `tests/test_bronze_loader.py`'s raw schema and
introduce a parallel Gold one, mirroring (but not importing —
see `loaders/bronze_loader.py`'s module docstring) `apps/backend`'s
`app/models/raw/*.py` and `app/models/gold/*.py`.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
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
from transformers.bronze_to_gold import run_transform
from validators.schema import (
    RawCircuitRef,
    RawConstructorRef,
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

PIPELINE_VERSION = "0.1.0"


def _raw_audit_columns() -> list[Column]:  # type: ignore[type-arg]
    return [
        Column("id", Uuid(), primary_key=True),
        Column("source", String(), nullable=False),
        Column("pipeline_version", String(), nullable=False),
        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    ]


def _gold_audit_columns() -> list[Column]:  # type: ignore[type-arg]
    return [
        Column("source", String(), nullable=False),
        Column("pipeline_version", String(), nullable=False),
        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    ]


def _build_raw_schema() -> MetaData:
    metadata = MetaData()
    Table(
        "raw_circuits",
        metadata,
        *_raw_audit_columns(),
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
        *_raw_audit_columns(),
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
        *_raw_audit_columns(),
        Column("constructor_id", String(), unique=True, nullable=False),
        Column("name", String(), nullable=False),
        Column("nationality", String()),
    )
    Table(
        "raw_sessions",
        metadata,
        *_raw_audit_columns(),
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
        *_raw_audit_columns(),
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
        *_raw_audit_columns(),
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
        *_raw_audit_columns(),
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
        UniqueConstraint(
            "source", "season", "round_number", "session_type", "time_offset_seconds"
        ),
    )
    return metadata


def _build_gold_schema() -> MetaData:
    metadata = MetaData()
    Table(
        "dim_season",
        metadata,
        Column("season_id", Uuid(), primary_key=True),
        *_gold_audit_columns(),
        Column("year", Integer(), unique=True, nullable=False),
        Column("race_count", Integer(), nullable=False),
        Column("sprint_count", Integer()),
        Column("champion_driver", String()),
        Column("champion_constructor", String()),
    )
    Table(
        "dim_constructor",
        metadata,
        Column("constructor_id", Uuid(), primary_key=True),
        *_gold_audit_columns(),
        Column("team_name", String(), nullable=False),
        Column("base_country", String()),
        Column("team_principal", String()),
        Column("power_unit", String()),
        Column("primary_color", String()),
        Column("secondary_color", String()),
        Column("logo", String()),
        Column("car_image", String()),
        Column("active", Boolean()),
    )
    Table(
        "dim_circuit",
        metadata,
        Column("circuit_id", Uuid(), primary_key=True),
        *_gold_audit_columns(),
        Column("name", String(), nullable=False),
        Column("country", String()),
        Column("city", String()),
        Column("length", Float()),
        Column("corners", Integer()),
        Column("drs_zones", Integer()),
        Column("lap_record", String()),
        Column("clockwise", Boolean()),
        Column("latitude", Float()),
        Column("longitude", Float()),
        Column("svg_track", String()),
    )
    Table(
        "dim_weather",
        metadata,
        Column("weather_id", Uuid(), primary_key=True),
        *_gold_audit_columns(),
        Column("air_temperature", Float()),
        Column("track_temperature", Float()),
        Column("humidity", Float()),
        Column("wind_speed", Float()),
        Column("wind_direction", Float()),
        Column("rainfall", Boolean()),
        Column("pressure", Float()),
        Column("track_status", String()),
    )
    Table(
        "dim_driver",
        metadata,
        Column("driver_id", Uuid(), primary_key=True),
        *_gold_audit_columns(),
        Column("driver_number", Integer()),
        Column("full_name", String(), nullable=False),
        Column("abbreviation", String()),
        Column("nationality", String()),
        Column("date_of_birth", String()),
        Column("team_id", Uuid(), ForeignKey("dim_constructor.constructor_id")),
        Column("rookie_season", Integer()),
        Column("world_titles", Integer()),
        Column("active", Boolean()),
    )
    Table(
        "dim_session",
        metadata,
        Column("session_id", Uuid(), primary_key=True),
        *_gold_audit_columns(),
        Column("season_id", Uuid(), ForeignKey("dim_season.season_id"), nullable=False),
        Column("round_number", Integer(), nullable=False),
        Column("race_name", String()),
        Column("session_type", String(), nullable=False),
        Column("date", String()),
        Column("weather_id", Uuid(), ForeignKey("dim_weather.weather_id")),
        Column("circuit_id", Uuid(), ForeignKey("dim_circuit.circuit_id")),
        UniqueConstraint("season_id", "round_number", "session_type"),
    )
    Table(
        "fct_results",
        metadata,
        Column("result_id", Uuid(), primary_key=True),
        *_gold_audit_columns(),
        Column("driver_id", Uuid(), ForeignKey("dim_driver.driver_id"), nullable=False),
        Column("session_id", Uuid(), ForeignKey("dim_session.session_id"), nullable=False),
        Column("grid_position", Float()),
        Column("finish_position", Float()),
        Column("points", Float()),
        Column("status", String()),
        Column("fastest_lap", Boolean()),
        Column("laps_completed", Integer()),
        UniqueConstraint("session_id", "driver_id"),
    )
    Table(
        "fct_laps",
        metadata,
        Column("lap_id", Uuid(), primary_key=True),
        *_gold_audit_columns(),
        Column("driver_id", Uuid(), ForeignKey("dim_driver.driver_id"), nullable=False),
        Column("session_id", Uuid(), ForeignKey("dim_session.session_id"), nullable=False),
        Column("lap_number", Float(), nullable=False),
        Column("lap_time", Float()),
        Column("sector_1", Float()),
        Column("sector_2", Float()),
        Column("sector_3", Float()),
        Column("compound", String()),
        Column("tyre_life", Float()),
        Column("position", Float()),
        Column("speed_trap", Float()),
        Column("drs", Boolean()),
        Column("pit_in", Boolean()),
        Column("pit_out", Boolean()),
        UniqueConstraint("session_id", "driver_id", "lap_number"),
    )
    Table(
        "fct_pitstop",
        metadata,
        Column("pitstop_id", Uuid(), primary_key=True),
        *_gold_audit_columns(),
        Column("driver_id", Uuid(), ForeignKey("dim_driver.driver_id"), nullable=False),
        Column("session_id", Uuid(), ForeignKey("dim_session.session_id"), nullable=False),
        Column("lap", Float(), nullable=False),
        Column("pit_duration", Float()),
        Column("stop_number", Integer()),
        Column("compound_before", String()),
        Column("compound_after", String()),
        UniqueConstraint("session_id", "driver_id", "lap"),
    )
    return metadata


@pytest.fixture
def raw_engine(tmp_path) -> Generator[Engine, None, None]:  # type: ignore[no-untyped-def]
    engine = create_engine(f"sqlite:///{tmp_path / 'raw.db'}")
    _build_raw_schema().create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def gold_engine(tmp_path) -> Generator[Engine, None, None]:  # type: ignore[no-untyped-def]
    engine = create_engine(f"sqlite:///{tmp_path / 'gold.db'}")
    _build_gold_schema().create_all(engine)
    yield engine
    engine.dispose()


def _seed_bahrain_round_1(raw_engine: Engine) -> None:
    """Seeds one full round of realistic, multi-source Bronze data: a
    circuit, a driver, a constructor, a Jolpica calendar entry, a FastF1
    schedule entry, FastF1 *and* Jolpica results for the same driver (with
    deliberately different points, so reconciliation tests can prove
    FastF1 wins), three laps (one of them a pit stop), and two weather
    samples.
    """
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
    bronze_loader.upsert_circuits_from_calendar(raw_engine, [calendar_entry], pipeline_version=PIPELINE_VERSION)
    bronze_loader.upsert_sessions_from_calendar(raw_engine, [calendar_entry], pipeline_version=PIPELINE_VERSION)

    schedule_event = RawEventSchedule(
        RoundNumber=1,
        EventName="Bahrain Grand Prix",
        Country="Bahrain",
        Location="Sakhir",
        EventDate="2024-03-02T00:00:00",
        F1ApiSupport=True,
    )
    bronze_loader.upsert_sessions_from_schedule(raw_engine, [schedule_event], pipeline_version=PIPELINE_VERSION)

    driver_standing = RawDriverStanding(
        position="1",
        points="25",
        wins="1",
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
    bronze_loader.upsert_drivers(raw_engine, [driver_standing.Driver], pipeline_version=PIPELINE_VERSION)
    bronze_loader.upsert_constructors(
        raw_engine, driver_standing.Constructors, pipeline_version=PIPELINE_VERSION
    )

    fastf1_result = RawSessionResult(
        DriverNumber="1",
        Abbreviation="VER",
        TeamName="Red Bull Racing",
        Position=1.0,
        GridPosition=1.0,
        Points=25.0,
        Status="Finished",
    )
    bronze_loader.upsert_results_fastf1(
        raw_engine,
        [fastf1_result],
        season=2024,
        round_number=1,
        session_type="R",
        pipeline_version=PIPELINE_VERSION,
    )

    # Deliberately different points (24 vs FastF1's 25) so reconciliation
    # tests can prove the FastF1 row wins.
    jolpica_result = RawRaceResult(
        number="1",
        position="1",
        positionText="1",
        points="24",
        grid="1",
        laps="57",
        status="Finished",
        Driver=driver_standing.Driver,
        Constructor=driver_standing.Constructors[0],
    )
    bronze_loader.upsert_results_jolpica(
        raw_engine, [jolpica_result], season=2024, round_number=1, pipeline_version=PIPELINE_VERSION
    )

    laps = [
        RawSessionLap(Driver="VER", LapNumber=1.0, LapTime=95.0, Compound="SOFT"),
        RawSessionLap(
            Driver="VER",
            LapNumber=18.0,
            LapTime=97.5,
            Compound="SOFT",
            PitInTime=1024.0,
            PitOutTime=1046.5,
        ),
        RawSessionLap(Driver="VER", LapNumber=19.0, LapTime=94.2, Compound="HARD"),
    ]
    bronze_loader.upsert_laps(
        raw_engine, laps, season=2024, round_number=1, session_type="R", pipeline_version=PIPELINE_VERSION
    )

    weather = [
        RawWeatherSample(
            Time=0.0, AirTemp=24.0, TrackTemp=30.0, Humidity=40.0, Pressure=1008.0, Rainfall=False,
            WindDirection=180.0, WindSpeed=1.0,
        ),
        RawWeatherSample(
            Time=60.0, AirTemp=26.0, TrackTemp=32.0, Humidity=42.0, Pressure=1009.0, Rainfall=False,
            WindDirection=182.0, WindSpeed=1.4,
        ),
    ]
    bronze_loader.upsert_weather(
        raw_engine, weather, season=2024, round_number=1, session_type="R", pipeline_version=PIPELINE_VERSION
    )


def _table(engine: Engine, name: str) -> Table:
    metadata = MetaData()
    return Table(name, metadata, autoload_with=engine)


class TestRunTransform:
    def test_dim_circuit_is_populated(self, raw_engine: Engine, gold_engine: Engine) -> None:
        _seed_bahrain_round_1(raw_engine)
        run_transform(raw_engine, gold_engine, season=2024, pipeline_version=PIPELINE_VERSION)

        table = _table(gold_engine, "dim_circuit")
        with gold_engine.connect() as connection:
            row = connection.execute(select(table)).mappings().one()
        assert row["name"] == "Bahrain International Circuit"
        assert row["country"] == "Bahrain"
        assert row["latitude"] == pytest.approx(26.0325)

    def test_dim_driver_resolves_team_and_abbreviation(
        self, raw_engine: Engine, gold_engine: Engine
    ) -> None:
        _seed_bahrain_round_1(raw_engine)
        run_transform(raw_engine, gold_engine, season=2024, pipeline_version=PIPELINE_VERSION)

        drivers = _table(gold_engine, "dim_driver")
        constructors = _table(gold_engine, "dim_constructor")
        with gold_engine.connect() as connection:
            driver_row = connection.execute(select(drivers)).mappings().one()
            constructor_row = connection.execute(select(constructors)).mappings().one()

        assert driver_row["full_name"] == "Max Verstappen"
        assert driver_row["abbreviation"] == "VER"
        assert driver_row["team_id"] == constructor_row["constructor_id"]
        assert constructor_row["team_name"] == "Red Bull Racing"

    def test_dim_season_race_count_and_champion(
        self, raw_engine: Engine, gold_engine: Engine
    ) -> None:
        _seed_bahrain_round_1(raw_engine)
        run_transform(raw_engine, gold_engine, season=2024, pipeline_version=PIPELINE_VERSION)

        table = _table(gold_engine, "dim_season")
        with gold_engine.connect() as connection:
            row = connection.execute(select(table)).mappings().one()

        assert row["year"] == 2024
        assert row["race_count"] == 1
        assert row["champion_driver"] == "Max Verstappen"
        assert row["champion_constructor"] == "Red Bull Racing"

    def test_dim_driver_world_titles_finalized(
        self, raw_engine: Engine, gold_engine: Engine
    ) -> None:
        _seed_bahrain_round_1(raw_engine)
        run_transform(raw_engine, gold_engine, season=2024, pipeline_version=PIPELINE_VERSION)

        table = _table(gold_engine, "dim_driver")
        with gold_engine.connect() as connection:
            row = connection.execute(select(table)).mappings().one()
        assert row["world_titles"] == 1

    def test_fct_results_prefers_fastf1_over_jolpica(
        self, raw_engine: Engine, gold_engine: Engine
    ) -> None:
        _seed_bahrain_round_1(raw_engine)
        run_transform(raw_engine, gold_engine, season=2024, pipeline_version=PIPELINE_VERSION)

        table = _table(gold_engine, "fct_results")
        with gold_engine.connect() as connection:
            rows = connection.execute(select(table)).mappings().all()

        assert len(rows) == 1  # exactly one row, not two (FastF1 + Jolpica)
        assert rows[0]["points"] == 25.0  # FastF1's value, not Jolpica's 24.0
        assert rows[0]["fastest_lap"] is True  # VER's only session, so trivially fastest
        assert rows[0]["laps_completed"] == 3

    def test_fct_laps_and_fct_pitstop(self, raw_engine: Engine, gold_engine: Engine) -> None:
        _seed_bahrain_round_1(raw_engine)
        run_transform(raw_engine, gold_engine, season=2024, pipeline_version=PIPELINE_VERSION)

        laps = _table(gold_engine, "fct_laps")
        pitstops = _table(gold_engine, "fct_pitstop")
        with gold_engine.connect() as connection:
            lap_rows = connection.execute(select(laps)).mappings().all()
            pitstop_rows = connection.execute(select(pitstops)).mappings().all()

        assert len(lap_rows) == 3
        assert len(pitstop_rows) == 1
        assert pitstop_rows[0]["lap"] == 18.0
        assert pitstop_rows[0]["pit_duration"] == pytest.approx(22.5)
        assert pitstop_rows[0]["compound_before"] == "SOFT"
        assert pitstop_rows[0]["compound_after"] == "SOFT"

    def test_dim_session_links_weather_and_circuit(
        self, raw_engine: Engine, gold_engine: Engine
    ) -> None:
        _seed_bahrain_round_1(raw_engine)
        run_transform(raw_engine, gold_engine, season=2024, pipeline_version=PIPELINE_VERSION)

        sessions = _table(gold_engine, "dim_session")
        weather = _table(gold_engine, "dim_weather")
        circuits = _table(gold_engine, "dim_circuit")
        with gold_engine.connect() as connection:
            session_row = connection.execute(select(sessions)).mappings().one()
            weather_row = connection.execute(select(weather)).mappings().one()
            circuit_row = connection.execute(select(circuits)).mappings().one()

        assert session_row["weather_id"] == weather_row["weather_id"]
        assert session_row["circuit_id"] == circuit_row["circuit_id"]
        assert weather_row["air_temperature"] == pytest.approx(25.0)  # average of 24.0 and 26.0
        assert weather_row["rainfall"] is False

    def test_rerunning_transform_is_idempotent_and_preserves_finalized_fields(
        self, raw_engine: Engine, gold_engine: Engine
    ) -> None:
        """The core regression this guards against: `_transform_season_shell`
        and `_transform_drivers` upsert on every run, and must never wipe
        out `_finalize_season_champion`/`_finalize_driver_world_titles`'s
        work back to `NULL` when the whole pipeline runs a second time."""
        _seed_bahrain_round_1(raw_engine)
        run_transform(raw_engine, gold_engine, season=2024, pipeline_version=PIPELINE_VERSION)
        run_transform(raw_engine, gold_engine, season=2024, pipeline_version="0.2.0")

        season_table = _table(gold_engine, "dim_season")
        driver_table = _table(gold_engine, "dim_driver")
        result_table = _table(gold_engine, "fct_results")
        lap_table = _table(gold_engine, "fct_laps")
        with gold_engine.connect() as connection:
            season_row = connection.execute(select(season_table)).mappings().one()
            driver_row = connection.execute(select(driver_table)).mappings().one()
            result_rows = connection.execute(select(result_table)).mappings().all()
            lap_rows = connection.execute(select(lap_table)).mappings().all()

        assert season_row["champion_driver"] == "Max Verstappen"  # not wiped to NULL
        assert driver_row["world_titles"] == 1  # not wiped to NULL
        assert len(result_rows) == 1  # not duplicated
        assert len(lap_rows) == 3  # not duplicated
        assert season_row["pipeline_version"] == "0.2.0"  # did pick up the second run's value
