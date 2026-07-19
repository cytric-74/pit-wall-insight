"""Writes validated records into the raw/bronze database's tables.

Purpose
-------
This is the one place in `apps/ingestion` that talks to a database. Every
function here takes a batch of already-validated records (Pydantic model
instances from `validators/schema.py`) and upserts them into the matching
`raw_*` table — created ahead of time by `apps/backend`'s Alembic migration
(`alembic/versions/bc6a4663b61a_create_raw_bronze_tables.py`).

Architecture: no cross-app import
----------------------------------
`apps/backend` owns the `raw_*` table *definitions* (SQLAlchemy ORM models
in `app/models/raw/`) and their migration. `apps/ingestion` is a separate
deployable app and deliberately does not import that package — the two
apps have independent dependency sets and release lifecycles, and nothing
about loading rows into an existing table requires knowing the original
ORM class, only the table's structure. Instead, every table this module
writes to is *reflected* at runtime via SQLAlchemy Core
(`Table(name, metadata, autoload_with=engine)`): this module's only
assumption about `apps/backend` is that its migration has already run
against the target database. Table/column names are still shared knowledge
between the two apps (they always would be, whichever approach was taken —
both sides must agree on what a "raw_results row" looks like), but there is
no Python import dependency, so the two apps can be developed, tested, and
deployed independently.

The one wrinkle reflection introduces: PostgreSQL has a native `UUID`
column type that reflects back as a UUID-aware SQLAlchemy type
automatically, but SQLite (used only in this project's tests, since there's
no Postgres available in this environment) has no native UUID type, so a
column created via SQLAlchemy's portable `Uuid()` type reflects back from
SQLite as a plain `CHAR`/`TEXT` column — losing the Python-level UUID
(de)serialization that only the original `Uuid()` type object provides.
`_reflect_table` works around this by passing an explicit `Column("id",
Uuid())` override alongside `autoload_with=engine`; SQLAlchemy prefers
explicitly-passed columns over reflected ones of the same name, so `id` is
treated identically as a UUID regardless of which dialect is running
underneath.

Idempotency
-----------
Every row's `id` is a deterministic UUID derived from its natural key
(`utils.ids.generate_id`), and every upsert targets that same natural key's
unique constraint (`conflict_columns`) — re-running ingestion for a season
that was already loaded updates existing rows in place rather than
duplicating them (docs/06_DATA_ENGINEERING.md: "Incremental Loading...
Only new sessions are inserted").

Never merges across sources
----------------------------
FastF1 and Jolpica-F1 rows for what is conceptually "the same" session or
result are *not* combined here — every `raw_results`/`raw_sessions` row
carries a `source` column, and both sources' rows for the same
season/round coexist. Deciding which to prefer is Gold-layer work for a
future phase (see `app/models/raw/__init__.py` on the backend side for the
full rationale).
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sqlalchemy import Column, Table, Uuid, create_engine
from sqlalchemy.engine import Engine

from utils.db import reflect_table, upsert
from utils.ids import generate_id
from validators.schema import (
    RawConstructorRef,
    RawDriverRef,
    RawEventSchedule,
    RawRaceCalendarEntry,
    RawRaceResult,
    RawSessionLap,
    RawSessionResult,
    RawWeatherSample,
)


def create_bronze_engine(database_url: str) -> Engine:
    """Create a sync SQLAlchemy engine for the raw/bronze database.

    A thin wrapper rather than callers using `create_engine` directly, so
    every engine this pipeline creates is built the same way (and so a
    future connection-pooling tweak has exactly one call site to change).
    """
    return create_engine(database_url, pool_pre_ping=True)


def _reflect_table(engine: Engine, name: str) -> Table:
    """Reflect a `raw_*` table's structure from the live database.

    Thin wrapper around `utils.db.reflect_table`, fixing the override to
    Bronze's universal `id` primary key column — see that function's
    docstring for why the override is needed at all, and
    `transformers/bronze_to_gold.py` for the Gold-side equivalent, which
    needs a different override per table (entity-specific PK/FK names).
    """
    return reflect_table(engine, name, Column("id", Uuid(), primary_key=True))


def _upsert(
    engine: Engine, table: Table, rows: list[dict[str, Any]], conflict_columns: list[str]
) -> int:
    """Insert `rows` into `table`, updating in place on a natural-key conflict.

    Thin wrapper around `utils.db.upsert` — see that function's docstring
    for the full contract (idempotent upsert semantics, why `updated_at`
    is set explicitly, time complexity).
    """
    return upsert(engine, table, rows, conflict_columns)


# ---------------------------------------------------------------------------
# raw_circuits
# ---------------------------------------------------------------------------


def upsert_circuits_from_calendar(
    engine: Engine, calendar_entries: list[RawRaceCalendarEntry], *, pipeline_version: str
) -> int:
    """Extract and upsert the distinct circuits referenced by a season's calendar.

    De-duplicates by `circuitId` within the batch first (a season's
    calendar can reference the same circuit only once per round, but
    calling this across multiple seasons' calendars in the same run is
    common, and every call still only needs one row per circuit).
    """
    rows: dict[str, dict[str, Any]] = {}
    for entry in calendar_entries:
        circuit = entry.Circuit
        rows[circuit.circuitId] = {
            "id": generate_id("circuit", circuit.circuitId),
            "source": "jolpica",
            "pipeline_version": pipeline_version,
            "circuit_id": circuit.circuitId,
            "circuit_name": circuit.circuitName,
            "locality": circuit.Location.locality,
            "country": circuit.Location.country,
            "latitude": circuit.Location.lat,
            "longitude": circuit.Location.long,
        }
    table = _reflect_table(engine, "raw_circuits")
    return _upsert(engine, table, list(rows.values()), conflict_columns=["circuit_id"])


# ---------------------------------------------------------------------------
# raw_drivers
# ---------------------------------------------------------------------------


def _driver_row(driver: RawDriverRef, pipeline_version: str) -> dict[str, Any]:
    return {
        "id": generate_id("driver", driver.driverId),
        "source": "jolpica",
        "pipeline_version": pipeline_version,
        "driver_id": driver.driverId,
        "code": driver.code,
        "given_name": driver.givenName,
        "family_name": driver.familyName,
        "date_of_birth": driver.dateOfBirth,
        "nationality": driver.nationality,
    }


def upsert_drivers(engine: Engine, drivers: Iterable[RawDriverRef], *, pipeline_version: str) -> int:
    """Upsert distinct drivers (de-duplicated by `driverId`) from any batch of nested Driver refs.

    Takes already-extracted `RawDriverRef` objects rather than a specific
    parent record type, since drivers appear nested inside both driver
    standings (`RawDriverStanding.Driver`) and race results
    (`RawRaceResult.Driver`) — callers pull out whichever they have (see
    `main.py`'s `_load_jolpica_driver_standings` /
    `_load_jolpica_race_results`) so this function stays usable from both.
    """
    rows = {driver.driverId: _driver_row(driver, pipeline_version) for driver in drivers}
    table = _reflect_table(engine, "raw_drivers")
    return _upsert(engine, table, list(rows.values()), conflict_columns=["driver_id"])


# ---------------------------------------------------------------------------
# raw_constructors
# ---------------------------------------------------------------------------


def _constructor_row(constructor: RawConstructorRef, pipeline_version: str) -> dict[str, Any]:
    return {
        "id": generate_id("constructor", constructor.constructorId),
        "source": "jolpica",
        "pipeline_version": pipeline_version,
        "constructor_id": constructor.constructorId,
        "name": constructor.name,
        "nationality": constructor.nationality,
    }


def upsert_constructors(
    engine: Engine, constructors: Iterable[RawConstructorRef], *, pipeline_version: str
) -> int:
    """Upsert distinct constructors (de-duplicated by `constructorId`) from any batch of nested Constructor refs.

    Same rationale as `upsert_drivers`: constructors appear nested inside
    constructor standings, driver standings (a driver's current team(s)),
    and race results.
    """
    rows = {
        constructor.constructorId: _constructor_row(constructor, pipeline_version)
        for constructor in constructors
    }
    table = _reflect_table(engine, "raw_constructors")
    return _upsert(engine, table, list(rows.values()), conflict_columns=["constructor_id"])


# ---------------------------------------------------------------------------
# raw_sessions
# ---------------------------------------------------------------------------


def upsert_sessions_from_schedule(
    engine: Engine, schedule: list[RawEventSchedule], *, pipeline_version: str
) -> int:
    """Upsert one `raw_sessions` row per FastF1 schedule entry (source="fastf1")."""
    rows = [
        {
            "id": generate_id("session", f"fastf1:{event.RoundNumber}"),
            "source": "fastf1",
            "pipeline_version": pipeline_version,
            "season": _season_from_event_date(event.EventDate),
            "round_number": event.RoundNumber,
            "race_name": event.EventName,
            "country": event.Country,
            "location": event.Location,
            "event_date": event.EventDate,
            "f1_api_support": event.F1ApiSupport,
        }
        for event in schedule
    ]
    table = _reflect_table(engine, "raw_sessions")
    return _upsert(
        engine, table, rows, conflict_columns=["source", "season", "round_number"]
    )


def upsert_sessions_from_calendar(
    engine: Engine, calendar_entries: list[RawRaceCalendarEntry], *, pipeline_version: str
) -> int:
    """Upsert one `raw_sessions` row per Jolpica calendar entry (source="jolpica")."""
    rows = [
        {
            "id": generate_id("session", f"jolpica:{entry.season}:{entry.round}"),
            "source": "jolpica",
            "pipeline_version": pipeline_version,
            "season": int(entry.season),
            "round_number": int(entry.round),
            "race_name": entry.raceName,
            "country": entry.Circuit.Location.country,
            "location": entry.Circuit.Location.locality,
            "event_date": entry.date,
            "f1_api_support": None,
        }
        for entry in calendar_entries
    ]
    table = _reflect_table(engine, "raw_sessions")
    return _upsert(
        engine, table, rows, conflict_columns=["source", "season", "round_number"]
    )


def _season_from_event_date(event_date: str | None) -> int:
    """Extract a season year from a FastF1 `EventDate` ISO string.

    FastF1's event schedule rows don't carry an explicit `season`/`year`
    field of their own — the season is implicit in which schedule was
    requested (`get_event_schedule(year)`), but by the time a row reaches
    this loader that context has already been flattened away into the
    record itself. Parsing it back out of `EventDate` (always populated for
    a real event) avoids requiring every caller of
    `upsert_sessions_from_schedule` to separately thread a `season`
    parameter through just to repeat what the date already encodes.
    """
    if event_date is None:
        raise ValueError("Cannot derive a season from a schedule entry with no EventDate")
    return int(event_date[:4])


# ---------------------------------------------------------------------------
# raw_results
# ---------------------------------------------------------------------------


def upsert_results_fastf1(
    engine: Engine,
    results: list[RawSessionResult],
    *,
    season: int,
    round_number: int,
    session_type: str,
    pipeline_version: str,
) -> int:
    rows = [
        {
            "id": generate_id(
                "result", f"fastf1:{season}:{round_number}:{session_type}:{result.DriverNumber}"
            ),
            "source": "fastf1",
            "pipeline_version": pipeline_version,
            "season": season,
            "round_number": round_number,
            "session_type": session_type,
            "driver_ref": result.DriverNumber,
            "position": result.Position,
            "points": result.Points,
            "status": result.Status,
            "grid_position": result.GridPosition,
            "driver_code": result.Abbreviation,
            "constructor_ref": result.TeamName,
        }
        for result in results
    ]
    table = _reflect_table(engine, "raw_results")
    return _upsert(
        engine,
        table,
        rows,
        conflict_columns=["source", "season", "round_number", "session_type", "driver_ref"],
    )


def upsert_results_jolpica(
    engine: Engine, results: list[RawRaceResult], *, season: int, round_number: int, pipeline_version: str
) -> int:
    """Upsert Jolpica race results — always `session_type="R"`, since Jolpica only reports race classifications."""
    rows = [
        {
            "id": generate_id(
                "result", f"jolpica:{season}:{round_number}:R:{result.Driver.driverId}"
            ),
            "source": "jolpica",
            "pipeline_version": pipeline_version,
            "season": season,
            "round_number": round_number,
            "session_type": "R",
            "driver_ref": result.Driver.driverId,
            "position": float(result.position),
            "points": float(result.points),
            "status": result.status,
            "grid_position": float(result.grid),
            # No `driver_code` needed: `driver_ref` already *is* the Jolpica
            # `driverId` that `raw_drivers.driver_id` is keyed on directly.
            "driver_code": None,
            "constructor_ref": result.Constructor.constructorId,
        }
        for result in results
    ]
    table = _reflect_table(engine, "raw_results")
    return _upsert(
        engine,
        table,
        rows,
        conflict_columns=["source", "season", "round_number", "session_type", "driver_ref"],
    )


# ---------------------------------------------------------------------------
# raw_laps
# ---------------------------------------------------------------------------


def upsert_laps(
    engine: Engine,
    laps: list[RawSessionLap],
    *,
    season: int,
    round_number: int,
    session_type: str,
    pipeline_version: str,
) -> int:
    rows = [
        {
            "id": generate_id(
                "lap",
                f"fastf1:{season}:{round_number}:{session_type}:{lap.Driver}:{lap.LapNumber}",
            ),
            "source": "fastf1",
            "pipeline_version": pipeline_version,
            "season": season,
            "round_number": round_number,
            "session_type": session_type,
            "driver_ref": lap.Driver,
            "lap_number": lap.LapNumber,
            "lap_time": lap.LapTime,
            "sector_1_time": lap.Sector1Time,
            "sector_2_time": lap.Sector2Time,
            "sector_3_time": lap.Sector3Time,
            "compound": lap.Compound,
            "tyre_life": lap.TyreLife,
            "stint": lap.Stint,
            "pit_in_time": lap.PitInTime,
            "pit_out_time": lap.PitOutTime,
            "position": lap.Position,
        }
        for lap in laps
    ]
    table = _reflect_table(engine, "raw_laps")
    return _upsert(
        engine,
        table,
        rows,
        conflict_columns=[
            "source",
            "season",
            "round_number",
            "session_type",
            "driver_ref",
            "lap_number",
        ],
    )


# ---------------------------------------------------------------------------
# raw_weather
# ---------------------------------------------------------------------------


def upsert_weather(
    engine: Engine,
    samples: list[RawWeatherSample],
    *,
    season: int,
    round_number: int,
    session_type: str,
    pipeline_version: str,
) -> int:
    rows = [
        {
            "id": generate_id(
                "weather", f"fastf1:{season}:{round_number}:{session_type}:{sample.Time}"
            ),
            "source": "fastf1",
            "pipeline_version": pipeline_version,
            "season": season,
            "round_number": round_number,
            "session_type": session_type,
            "time_offset_seconds": sample.Time,
            "air_temp": sample.AirTemp,
            "track_temp": sample.TrackTemp,
            "humidity": sample.Humidity,
            "pressure": sample.Pressure,
            "wind_direction": sample.WindDirection,
            "wind_speed": sample.WindSpeed,
            "rainfall": sample.Rainfall,
        }
        for sample in samples
    ]
    table = _reflect_table(engine, "raw_weather")
    return _upsert(
        engine,
        table,
        rows,
        conflict_columns=["source", "season", "round_number", "session_type", "time_offset_seconds"],
    )


__all__ = [
    "create_bronze_engine",
    "upsert_circuits_from_calendar",
    "upsert_constructors",
    "upsert_drivers",
    "upsert_laps",
    "upsert_results_fastf1",
    "upsert_results_jolpica",
    "upsert_sessions_from_calendar",
    "upsert_sessions_from_schedule",
    "upsert_weather",
]
