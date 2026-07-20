"""Transforms one season's Bronze data into Gold dimensions and facts.

Purpose
-------
`run_transform` is the single public entrypoint: given a season, it reads
every relevant `raw_*` row from the Bronze database and upserts the
corresponding `dim_*`/`fct_*` rows into the Gold database, in a fixed
internal order (see that function's docstring for exactly why the order
matters). Every other function in this module is private and is only ever
correct when called in that order — `run_transform` is what guarantees
that, so nothing outside this module should call the `_transform_*`
helpers directly.

Reconciliation happens here, not in Bronze
-------------------------------------------
`loaders/bronze_loader.py` never merges FastF1 and Jolpica-F1 rows for the
same real-world race — this module is where that finally happens.
`fct_results` keeps exactly one row per driver per session: a FastF1 row
when one exists, a Jolpica row only as a fallback (matching the
source-of-truth plan this pipeline was designed against — FastF1 has
richer per-session data but only reliably exists from 2018 onward; Jolpica
covers every season back to 1950 but only race-level classifications).

IDs
---
Every Gold dimension row that corresponds 1:1 with a deduplicated Bronze
row (`dim_circuit`, `dim_constructor`, `dim_driver`) reuses that Bronze
row's own `id` directly, rather than generating a new one — both are
already the same deterministic UUID
(`utils.ids.generate_id(<namespace>, <natural key>)`), so no join or
lookup table is needed to connect a Gold dimension back to its Bronze
source. Gold-only entities with no single Bronze counterpart (`dim_season`,
`dim_session`, `dim_weather`, and every fact table) get their own
deterministic IDs, derived from the (season, round, session_type, ...)
tuple that identifies them — see each function below for its exact key.
"""

from __future__ import annotations

import itertools
import logging
import statistics
import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy import Column, Uuid, func, select
from sqlalchemy.engine import Engine

from utils.db import reflect_table, upsert
from utils.ids import generate_id

logger = logging.getLogger("ingestion.transformers")

_TRANSFORM_SOURCE = "transform"


def _to_float(value: str | None) -> float | None:
    """Best-effort string-to-float parse, `None` on anything unparsable.

    Used for Jolpica's coordinate strings (`raw_circuits.latitude`/
    `longitude`) — Bronze keeps them as raw strings (see
    `app/models/raw/circuit.py`); casting to a real number is exactly the
    kind of type-cleaning work this Gold transform is responsible for.
    """
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _to_date(value: str | None) -> date | None:
    """Best-effort ISO-date-string-to-`date` parse, `None` on anything unparsable."""
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _transform_circuits(raw_engine: Engine, gold_engine: Engine, *, pipeline_version: str) -> int:
    """Upsert `dim_circuit` from every `raw_circuits` row (global — not scoped to one season)."""
    raw_circuits = reflect_table(raw_engine, "raw_circuits", Column("id", Uuid(), primary_key=True))
    with raw_engine.connect() as connection:
        rows = connection.execute(select(raw_circuits)).mappings().all()

    gold_rows = [
        {
            "circuit_id": row["id"],
            "source": _TRANSFORM_SOURCE,
            "pipeline_version": pipeline_version,
            "name": row["circuit_name"],
            "country": row["country"],
            "city": row["locality"],
            # length/corners/drs_zones/lap_record/clockwise/svg_track: no
            # source in this pipeline yet (see app/models/gold/circuit.py).
            "length": None,
            "corners": None,
            "drs_zones": None,
            "lap_record": None,
            "clockwise": None,
            "latitude": _to_float(row["latitude"]),
            "longitude": _to_float(row["longitude"]),
            "svg_track": None,
        }
        for row in rows
    ]
    dim_circuit = reflect_table(
        gold_engine, "dim_circuit", Column("circuit_id", Uuid(), primary_key=True)
    )
    return upsert(gold_engine, dim_circuit, gold_rows, conflict_columns=["circuit_id"])


def _transform_constructors(
    raw_engine: Engine, gold_engine: Engine, *, pipeline_version: str
) -> int:
    """Upsert `dim_constructor` from every `raw_constructors` row (global).

    `active` is best-effort: `True` if this constructor's `constructor_id`
    appears as a Jolpica-sourced `raw_results.constructor_ref` in the most
    recent season present in Bronze, `None` (unknown, not `False`) if no
    results have been loaded at all yet.
    """
    raw_constructors = reflect_table(
        raw_engine, "raw_constructors", Column("id", Uuid(), primary_key=True)
    )
    raw_results = reflect_table(raw_engine, "raw_results", Column("id", Uuid(), primary_key=True))

    with raw_engine.connect() as connection:
        constructor_rows = connection.execute(select(raw_constructors)).mappings().all()
        latest_season = connection.execute(select(func.max(raw_results.c.season))).scalar_one_or_none()
        active_refs: set[str] = set()
        if latest_season is not None:
            active_refs = {
                row[0]
                for row in connection.execute(
                    select(raw_results.c.constructor_ref)
                    .where(
                        raw_results.c.season == latest_season,
                        raw_results.c.source == "jolpica",
                    )
                    .distinct()
                )
                if row[0] is not None
            }

    gold_rows = [
        {
            "constructor_id": row["id"],
            "source": _TRANSFORM_SOURCE,
            "pipeline_version": pipeline_version,
            "team_name": row["name"],
            "base_country": row["nationality"],
            # team_principal/power_unit/primary_color/secondary_color/logo/
            # car_image: no source in this pipeline (see
            # app/models/gold/constructor.py).
            "team_principal": None,
            "power_unit": None,
            "primary_color": None,
            "secondary_color": None,
            "logo": None,
            "car_image": None,
            "active": (row["constructor_id"] in active_refs) if latest_season is not None else None,
        }
        for row in constructor_rows
    ]
    dim_constructor = reflect_table(
        gold_engine, "dim_constructor", Column("constructor_id", Uuid(), primary_key=True)
    )
    return upsert(gold_engine, dim_constructor, gold_rows, conflict_columns=["constructor_id"])


def _transform_drivers(raw_engine: Engine, gold_engine: Engine, *, pipeline_version: str) -> int:
    """Upsert `dim_driver` from every `raw_drivers` row (global).

    `team_id` is resolved from whichever `raw_results` row for this driver
    has the highest (season, round_number) and a non-null
    `constructor_ref` — i.e. their most recent known team. `rookie_season`
    is the minimum season this driver appears in across `raw_results` at
    all (only as complete as the seasons loaded so far). `world_titles` is
    intentionally left `None` here — see `_finalize_driver_world_titles`,
    which sets it in a separate pass after `dim_season` exists, using
    `update_columns` so this function re-running later never wipes that
    finalized value back out (see `utils.db.upsert`'s docstring for why
    that matters).
    """
    raw_drivers = reflect_table(raw_engine, "raw_drivers", Column("id", Uuid(), primary_key=True))
    raw_results = reflect_table(raw_engine, "raw_results", Column("id", Uuid(), primary_key=True))
    raw_constructors = reflect_table(
        raw_engine, "raw_constructors", Column("id", Uuid(), primary_key=True)
    )

    with raw_engine.connect() as connection:
        driver_rows = connection.execute(select(raw_drivers)).mappings().all()
        latest_season = connection.execute(select(func.max(raw_results.c.season))).scalar_one_or_none()

        # Fetched once and grouped in Python (matching `_transform_laps`/
        # `_transform_results`) rather than one query per driver — the
        # original per-driver `SELECT ... WHERE driver_ref = ? OR
        # driver_code = ?` was an N+1 query pattern that scaled linearly
        # with the (all-time, not season-scoped) driver count (Phase 7
        # audit, High).
        results_by_ref: dict[Any, list[dict[str, Any]]] = defaultdict(list)
        results_by_code: dict[Any, list[dict[str, Any]]] = defaultdict(list)
        for row in connection.execute(select(raw_results)).mappings().all():
            result_row = dict(row)
            results_by_ref[result_row["driver_ref"]].append(result_row)
            if result_row["driver_code"] is not None:
                results_by_code[result_row["driver_code"]].append(result_row)

        constructor_id_by_ref = {
            row["constructor_id"]: row["id"]
            for row in connection.execute(select(raw_constructors)).mappings().all()
        }
        constructor_id_by_name = {
            row["name"]: row["id"]
            for row in connection.execute(select(raw_constructors)).mappings().all()
        }

        gold_rows: list[dict[str, Any]] = []
        for driver in driver_rows:
            natural_key = driver["driver_id"]
            code = driver["code"]

            # A row can satisfy both the driver_ref and driver_code match,
            # so results are merged into a dict keyed by row id — the same
            # de-duplication the original `OR`-based query gave for free.
            matches_by_id = {match["id"]: match for match in results_by_ref.get(natural_key, [])}
            if code:
                matches_by_id.update(
                    {match["id"]: match for match in results_by_code.get(code, [])}
                )
            matches = list(matches_by_id.values())

            rookie_season = min((match["season"] for match in matches), default=None)
            active = latest_season is not None and any(
                match["season"] == latest_season for match in matches
            )

            # `constructor_ref` means different things per source: Jolpica's
            # is a stable id that joins directly against
            # `raw_constructors.constructor_id`; FastF1's is a free-text
            # team name (`TeamName`) with no stable id at the results
            # level, joinable only against `raw_constructors.name` — and
            # only as a fuzzy fallback, since two sources' spellings of a
            # team's name aren't guaranteed to match exactly. Jolpica
            # candidates are tried first for this reason, not merely
            # picked by whichever row happens to sort last.
            team_id: uuid.UUID | None = None
            jolpica_candidates = sorted(
                (
                    match
                    for match in matches
                    if match["constructor_ref"] and match["source"] == "jolpica"
                ),
                key=lambda match: (match["season"], match["round_number"]),
            )
            fastf1_candidates = sorted(
                (
                    match
                    for match in matches
                    if match["constructor_ref"] and match["source"] == "fastf1"
                ),
                key=lambda match: (match["season"], match["round_number"]),
            )
            if jolpica_candidates:
                constructor_ref = jolpica_candidates[-1]["constructor_ref"]
                team_id = constructor_id_by_ref.get(constructor_ref)
            elif fastf1_candidates:
                constructor_ref = fastf1_candidates[-1]["constructor_ref"]
                team_id = constructor_id_by_name.get(constructor_ref)

            gold_rows.append(
                {
                    "driver_id": driver["id"],
                    "source": _TRANSFORM_SOURCE,
                    "pipeline_version": pipeline_version,
                    # No source distinguishes a driver's permanent car
                    # number from a given race's grid number in this
                    # pipeline yet (see app/models/gold/driver.py).
                    "driver_number": None,
                    "full_name": f"{driver['given_name']} {driver['family_name']}",
                    "abbreviation": code,
                    "nationality": driver["nationality"],
                    "date_of_birth": _to_date(driver["date_of_birth"]),
                    "team_id": team_id,
                    "rookie_season": rookie_season,
                    "world_titles": None,
                    "active": active,
                }
            )

    dim_driver = reflect_table(
        gold_engine,
        "dim_driver",
        Column("driver_id", Uuid(), primary_key=True),
        Column("team_id", Uuid()),
    )
    return upsert(
        gold_engine,
        dim_driver,
        gold_rows,
        conflict_columns=["driver_id"],
        update_columns=[
            "pipeline_version",
            "driver_number",
            "full_name",
            "abbreviation",
            "nationality",
            "date_of_birth",
            "team_id",
            "rookie_season",
            "active",
        ],
    )


def _transform_season_shell(
    raw_engine: Engine, gold_engine: Engine, season: int, *, pipeline_version: str
) -> int:
    """Upsert `dim_season`'s `year`/`race_count`/`sprint_count` for one season.

    Deliberately does not touch `champion_driver`/`champion_constructor` —
    see `_finalize_season_champion`, which sets those in a later pass, and
    `utils.db.upsert`'s `update_columns` docstring for why this function
    must not overwrite them back to `NULL` on a later re-run.

    `race_count` counts distinct rounds in Jolpica's calendar
    (`raw_sessions` where `source="jolpica"`) — the authoritative full-
    season round list, independent of how many rounds have actually been
    transformed into Gold facts so far. `sprint_count` is best-effort: it
    only counts rounds where a Sprint/Sprint-Qualifying session has
    actually been *collected* (`raw_results`/`raw_laps` with
    `session_type` in `("S", "SQ")`), so it under-counts until those
    sessions are ingested.
    """
    raw_sessions = reflect_table(raw_engine, "raw_sessions", Column("id", Uuid(), primary_key=True))
    raw_results = reflect_table(raw_engine, "raw_results", Column("id", Uuid(), primary_key=True))

    with raw_engine.connect() as connection:
        race_count = connection.execute(
            select(func.count(func.distinct(raw_sessions.c.round_number))).where(
                raw_sessions.c.season == season, raw_sessions.c.source == "jolpica"
            )
        ).scalar_one()
        sprint_count = connection.execute(
            select(func.count(func.distinct(raw_results.c.round_number))).where(
                raw_results.c.season == season, raw_results.c.session_type.in_(("S", "SQ"))
            )
        ).scalar_one()

    season_id = generate_id("gold_season", str(season))
    dim_season = reflect_table(gold_engine, "dim_season", Column("season_id", Uuid(), primary_key=True))
    row = {
        "season_id": season_id,
        "source": _TRANSFORM_SOURCE,
        "pipeline_version": pipeline_version,
        "year": season,
        "race_count": race_count,
        "sprint_count": sprint_count,
    }
    return upsert(
        gold_engine,
        dim_season,
        [row],
        conflict_columns=["year"],
        update_columns=["pipeline_version", "race_count", "sprint_count"],
    )


def _transform_weather(raw_engine: Engine, gold_engine: Engine, season: int, *, pipeline_version: str) -> int:
    """Upsert one aggregated `dim_weather` row per (round, session_type) in this season.

    Grain note: `dim_weather` is a dimension (docs/07_DATABASE_SCHEMA.md's
    entity relationship diagram shows `dim_session` holding a single
    `weather_id`), not a time series — every `raw_weather` sample for a
    session (FastF1 samples roughly once a minute) is aggregated here into
    one representative row: averages for temperature/humidity/pressure/
    wind speed, and whether rain was recorded *at all* during the session.
    """
    raw_weather = reflect_table(raw_engine, "raw_weather", Column("id", Uuid(), primary_key=True))

    with raw_engine.connect() as connection:
        rows = connection.execute(
            select(raw_weather).where(raw_weather.c.season == season)
        ).mappings().all()

    grouped: dict[tuple[int, str], list[Any]] = defaultdict(list)
    for row in rows:
        grouped[(row["round_number"], row["session_type"])].append(row)

    gold_rows = []
    for (round_number, session_type), samples in grouped.items():
        weather_id = generate_id("gold_weather", f"{season}:{round_number}:{session_type}")

        def _average(field: str, samples: list[Any] = samples) -> float | None:
            values = [sample[field] for sample in samples if sample[field] is not None]
            return sum(values) / len(values) if values else None

        gold_rows.append(
            {
                "weather_id": weather_id,
                "source": _TRANSFORM_SOURCE,
                "pipeline_version": pipeline_version,
                "air_temperature": _average("air_temp"),
                "track_temperature": _average("track_temp"),
                "humidity": _average("humidity"),
                "wind_speed": _average("wind_speed"),
                "wind_direction": _average("wind_direction"),
                "rainfall": any(sample["rainfall"] for sample in samples),
                "pressure": _average("pressure"),
                "track_status": None,
            }
        )

    dim_weather = reflect_table(
        gold_engine, "dim_weather", Column("weather_id", Uuid(), primary_key=True)
    )
    # `dim_weather` has no natural-key business columns to conflict on
    # besides its own deterministic id — every row's `weather_id` already
    # encodes (season, round, session_type) uniquely, so the id itself is
    # both the primary key and the natural key here.
    return upsert(gold_engine, dim_weather, gold_rows, conflict_columns=["weather_id"])


def _transform_sessions(raw_engine: Engine, gold_engine: Engine, season: int, *, pipeline_version: str) -> int:
    """Upsert `dim_session` — one row per (season, round, session_type) actually recorded.

    Grain is derived from `raw_results`/`raw_laps` (both FastF1-sourced,
    both already carrying `session_type` at row level) rather than from
    `raw_sessions` (which is round-grain only — see
    `app/models/raw/session.py`). `circuit_id` is resolved by matching this
    round's Jolpica `raw_sessions` row's `location`/`country` text against
    `raw_circuits.locality`/`country` — a best-effort string match, `None`
    when nothing matches, since Bronze carries no direct round-to-circuit
    foreign key.
    """
    raw_results = reflect_table(raw_engine, "raw_results", Column("id", Uuid(), primary_key=True))
    raw_laps = reflect_table(raw_engine, "raw_laps", Column("id", Uuid(), primary_key=True))
    raw_sessions = reflect_table(raw_engine, "raw_sessions", Column("id", Uuid(), primary_key=True))
    raw_circuits = reflect_table(raw_engine, "raw_circuits", Column("id", Uuid(), primary_key=True))

    with raw_engine.connect() as connection:
        result_keys = connection.execute(
            select(raw_results.c.round_number, raw_results.c.session_type)
            .where(raw_results.c.season == season)
            .distinct()
        ).all()
        lap_keys = connection.execute(
            select(raw_laps.c.round_number, raw_laps.c.session_type)
            .where(raw_laps.c.season == season)
            .distinct()
        ).all()
        calendar_rows = connection.execute(
            select(raw_sessions).where(
                raw_sessions.c.season == season, raw_sessions.c.source == "jolpica"
            )
        ).mappings().all()
        circuit_rows = connection.execute(select(raw_circuits)).mappings().all()

    calendar_by_round = {row["round_number"]: row for row in calendar_rows}
    circuit_id_by_location = {
        (row["locality"], row["country"]): row["id"] for row in circuit_rows
    }

    session_type_keys = {(round_number, session_type) for round_number, session_type in (*result_keys, *lap_keys)}

    season_id = generate_id("gold_season", str(season))
    gold_rows = []
    for round_number, session_type in session_type_keys:
        session_id = generate_id("gold_session", f"{season}:{round_number}:{session_type}")
        weather_id = generate_id("gold_weather", f"{season}:{round_number}:{session_type}")
        calendar_row = calendar_by_round.get(round_number)
        circuit_id = None
        if calendar_row is not None:
            circuit_id = circuit_id_by_location.get(
                (calendar_row["location"], calendar_row["country"])
            )

        gold_rows.append(
            {
                "session_id": session_id,
                "source": _TRANSFORM_SOURCE,
                "pipeline_version": pipeline_version,
                "season_id": season_id,
                "round_number": round_number,
                "race_name": calendar_row["race_name"] if calendar_row is not None else None,
                "session_type": session_type,
                "date": calendar_row["event_date"] if calendar_row is not None else None,
                "weather_id": weather_id,
                "circuit_id": circuit_id,
            }
        )

    dim_session = reflect_table(
        gold_engine,
        "dim_session",
        Column("session_id", Uuid(), primary_key=True),
        Column("season_id", Uuid()),
        Column("weather_id", Uuid()),
        Column("circuit_id", Uuid()),
    )
    return upsert(
        gold_engine,
        dim_session,
        gold_rows,
        conflict_columns=["season_id", "round_number", "session_type"],
    )


def _transform_laps(raw_engine: Engine, gold_engine: Engine, season: int, *, pipeline_version: str) -> tuple[int, dict[tuple[int, str, uuid.UUID], list[dict[str, Any]]]]:
    """Upsert `fct_laps` for this season; returns the row count plus every
    lap grouped by (round, session_type, driver_id), which
    `_transform_results` and `_transform_pitstops` both need (fastest-lap/
    lap-count and pit-stop detection respectively) without re-querying
    Bronze themselves.
    """
    raw_laps = reflect_table(raw_engine, "raw_laps", Column("id", Uuid(), primary_key=True))
    raw_drivers = reflect_table(raw_engine, "raw_drivers", Column("id", Uuid(), primary_key=True))

    with raw_engine.connect() as connection:
        driver_id_by_code = {
            row["code"]: row["id"]
            for row in connection.execute(select(raw_drivers)).mappings().all()
            if row["code"] is not None
        }
        lap_rows = connection.execute(
            select(raw_laps).where(raw_laps.c.season == season).order_by(raw_laps.c.lap_number)
        ).mappings().all()

    grouped: dict[tuple[int, str, uuid.UUID], list[dict[str, Any]]] = defaultdict(list)
    gold_rows = []
    for lap in lap_rows:
        driver_id = driver_id_by_code.get(lap["driver_ref"])
        if driver_id is None:
            # No matching dim_driver — this driver was never seen in any
            # standings/results Jolpica data, so there's nothing to link
            # this lap to yet. Skipped rather than guessed at.
            continue

        session_id = generate_id(
            "gold_session", f"{season}:{lap['round_number']}:{lap['session_type']}"
        )
        grouped[(lap["round_number"], lap["session_type"], driver_id)].append(dict(lap))

        gold_rows.append(
            {
                "lap_id": generate_id(
                    "fct_lap",
                    f"{season}:{lap['round_number']}:{lap['session_type']}:{driver_id}:{lap['lap_number']}",
                ),
                "source": _TRANSFORM_SOURCE,
                "pipeline_version": pipeline_version,
                "driver_id": driver_id,
                "session_id": session_id,
                "lap_number": lap["lap_number"],
                "lap_time": lap["lap_time"],
                "sector_1": lap["sector_1_time"],
                "sector_2": lap["sector_2_time"],
                "sector_3": lap["sector_3_time"],
                "compound": lap["compound"],
                "tyre_life": lap["tyre_life"],
                "position": lap["position"],
                # speed_trap/drs: not collected by
                # validators.schema.RawSessionLap (see
                # app/models/gold/lap.py).
                "speed_trap": None,
                "drs": None,
                "pit_in": lap["pit_in_time"] is not None,
                "pit_out": lap["pit_out_time"] is not None,
            }
        )

    dim_lap = reflect_table(
        gold_engine,
        "fct_laps",
        Column("lap_id", Uuid(), primary_key=True),
        Column("driver_id", Uuid()),
        Column("session_id", Uuid()),
    )
    count = upsert(
        gold_engine, dim_lap, gold_rows, conflict_columns=["session_id", "driver_id", "lap_number"]
    )
    return count, grouped


def _transform_pitstops(
    gold_engine: Engine,
    season: int,
    laps_by_driver_session: dict[tuple[int, str, uuid.UUID], list[dict[str, Any]]],
    *,
    pipeline_version: str,
) -> int:
    """Upsert `fct_pitstop`, derived from the same lap groups `_transform_laps` already built.

    Detects a stop only when both `pit_in_time` and `pit_out_time` are set
    on the *same* lap row — see `app/models/gold/pitstop.py` for why a
    stop spanning two lap rows isn't currently detected.
    """
    gold_rows = []
    for (round_number, session_type, driver_id), laps in laps_by_driver_session.items():
        session_id = generate_id("gold_session", f"{season}:{round_number}:{session_type}")
        stop_number = 0
        previous_compound: str | None = None
        for lap in laps:
            compound_before = previous_compound
            previous_compound = lap["compound"]
            if lap["pit_in_time"] is None or lap["pit_out_time"] is None:
                continue
            stop_number += 1
            gold_rows.append(
                {
                    "pitstop_id": generate_id(
                        "fct_pitstop",
                        f"{season}:{round_number}:{session_type}:{driver_id}:{lap['lap_number']}",
                    ),
                    "source": _TRANSFORM_SOURCE,
                    "pipeline_version": pipeline_version,
                    "driver_id": driver_id,
                    "session_id": session_id,
                    "lap": lap["lap_number"],
                    "pit_duration": lap["pit_out_time"] - lap["pit_in_time"],
                    "stop_number": stop_number,
                    "compound_before": compound_before,
                    "compound_after": lap["compound"],
                }
            )

    dim_pitstop = reflect_table(
        gold_engine,
        "fct_pitstop",
        Column("pitstop_id", Uuid(), primary_key=True),
        Column("driver_id", Uuid()),
        Column("session_id", Uuid()),
    )
    return upsert(
        gold_engine, dim_pitstop, gold_rows, conflict_columns=["session_id", "driver_id", "lap"]
    )


def _transform_results(
    raw_engine: Engine,
    gold_engine: Engine,
    season: int,
    laps_by_driver_session: dict[tuple[int, str, uuid.UUID], list[dict[str, Any]]],
    *,
    pipeline_version: str,
) -> int:
    """Upsert `fct_results` for this season, reconciling FastF1 and Jolpica rows.

    Exactly one row per (round, session_type, driver): a FastF1-sourced
    row wins whenever one exists, a Jolpica-sourced row is used only as a
    fallback (Jolpica only ever reports `session_type="R"`, so it can only
    ever fall back for race sessions). `fastest_lap`/`laps_completed` come
    from `laps_by_driver_session` (already computed by `_transform_laps`)
    rather than a fresh Bronze query.
    """
    raw_results = reflect_table(raw_engine, "raw_results", Column("id", Uuid(), primary_key=True))
    raw_drivers = reflect_table(raw_engine, "raw_drivers", Column("id", Uuid(), primary_key=True))

    with raw_engine.connect() as connection:
        driver_id_by_code = {
            row["code"]: row["id"]
            for row in connection.execute(select(raw_drivers)).mappings().all()
            if row["code"] is not None
        }
        driver_id_by_natural_key = {
            row["driver_id"]: row["id"]
            for row in connection.execute(select(raw_drivers)).mappings().all()
        }
        result_rows = connection.execute(
            select(raw_results).where(raw_results.c.season == season)
        ).mappings().all()

    fastest_lap_time_by_session: dict[tuple[int, str], float] = {}
    for (round_number, session_type, _driver_id), laps in laps_by_driver_session.items():
        times = [lap["lap_time"] for lap in laps if lap["lap_time"] is not None]
        if not times:
            continue
        key = (round_number, session_type)
        fastest_lap_time_by_session[key] = min(fastest_lap_time_by_session.get(key, float("inf")), min(times))

    reconciled: dict[tuple[int, str, uuid.UUID], dict[str, Any]] = {}
    for row in result_rows:
        driver_id = (
            driver_id_by_code.get(row["driver_code"])
            if row["driver_code"]
            else driver_id_by_natural_key.get(row["driver_ref"])
        )
        if driver_id is None:
            continue
        result_key = (row["round_number"], row["session_type"], driver_id)
        if result_key in reconciled and reconciled[result_key]["source"] == "fastf1":
            continue  # a FastF1 row already won this key; Jolpica never overrides it.
        reconciled[result_key] = dict(row) | {"_driver_id": driver_id}

    gold_rows = []
    for (round_number, session_type, driver_id), reconciled_row in reconciled.items():
        session_id = generate_id("gold_session", f"{season}:{round_number}:{session_type}")
        laps = laps_by_driver_session.get((round_number, session_type, driver_id), [])
        driver_lap_times = [lap["lap_time"] for lap in laps if lap["lap_time"] is not None]
        session_fastest = fastest_lap_time_by_session.get((round_number, session_type))
        fastest_lap = (
            bool(driver_lap_times) and session_fastest is not None and min(driver_lap_times) == session_fastest
        )

        gold_rows.append(
            {
                "result_id": generate_id(
                    "fct_result", f"{season}:{round_number}:{session_type}:{driver_id}"
                ),
                "source": _TRANSFORM_SOURCE,
                "pipeline_version": pipeline_version,
                "driver_id": driver_id,
                "session_id": session_id,
                "grid_position": reconciled_row["grid_position"],
                "finish_position": reconciled_row["position"],
                "points": reconciled_row["points"],
                "status": reconciled_row["status"],
                "fastest_lap": fastest_lap if laps else None,
                "laps_completed": len(laps) if laps else None,
            }
        )

    fct_result = reflect_table(
        gold_engine,
        "fct_results",
        Column("result_id", Uuid(), primary_key=True),
        Column("driver_id", Uuid()),
        Column("session_id", Uuid()),
    )
    return upsert(
        gold_engine, fct_result, gold_rows, conflict_columns=["session_id", "driver_id"]
    )


def _finalize_season_champion(gold_engine: Engine, season: int, *, pipeline_version: str) -> None:
    """Set `dim_season.champion_driver`/`champion_constructor` from this run's own `fct_results`.

    Sums `fct_results.points` per driver across every `dim_session` in
    this season, takes the highest-scoring driver as `champion_driver`
    (via `dim_driver.full_name`) and their resolved `dim_driver.team_id`
    as `champion_constructor` (via `dim_constructor.team_name`). Only
    meaningful once every round of a completed season has been
    transformed — for an in-progress season this reflects "leader so far,"
    which is an honest, clearly-labeled partial result rather than a wrong
    one (see `app/models/gold/season.py`).
    """
    season_id = generate_id("gold_season", str(season))
    dim_session = reflect_table(
        gold_engine, "dim_session", Column("session_id", Uuid(), primary_key=True), Column("season_id", Uuid())
    )
    fct_result = reflect_table(
        gold_engine,
        "fct_results",
        Column("result_id", Uuid(), primary_key=True),
        Column("driver_id", Uuid()),
        Column("session_id", Uuid()),
    )
    dim_driver = reflect_table(
        gold_engine,
        "dim_driver",
        Column("driver_id", Uuid(), primary_key=True),
        Column("team_id", Uuid()),
    )
    dim_constructor = reflect_table(
        gold_engine, "dim_constructor", Column("constructor_id", Uuid(), primary_key=True)
    )
    dim_season = reflect_table(
        gold_engine,
        "dim_season",
        Column("season_id", Uuid(), primary_key=True),
        Column("champion_driver_id", Uuid()),
        Column("champion_constructor_id", Uuid()),
    )

    with gold_engine.connect() as connection:
        standings = connection.execute(
            select(
                dim_driver.c.driver_id,
                dim_driver.c.full_name,
                dim_driver.c.team_id,
                func.sum(fct_result.c.points).label("total_points"),
            )
            .select_from(fct_result)
            .join(dim_session, fct_result.c.session_id == dim_session.c.session_id)
            .join(dim_driver, fct_result.c.driver_id == dim_driver.c.driver_id)
            .where(dim_session.c.season_id == season_id)
            .group_by(dim_driver.c.driver_id, dim_driver.c.full_name, dim_driver.c.team_id)
            .order_by(func.sum(fct_result.c.points).desc())
            .limit(1)
        ).first()

        if standings is None:
            return

        champion_constructor = None
        if standings.team_id is not None:
            constructor_row = connection.execute(
                select(dim_constructor.c.team_name).where(
                    dim_constructor.c.constructor_id == standings.team_id
                )
            ).first()
            champion_constructor = constructor_row[0] if constructor_row is not None else None

        connection.execute(
            dim_season.update()
            .where(dim_season.c.season_id == season_id)
            .values(
                champion_driver=standings.full_name,
                champion_driver_id=standings.driver_id,
                champion_constructor=champion_constructor,
                champion_constructor_id=standings.team_id,
                updated_at=func.now(),
            )
        )
        connection.commit()


def _finalize_driver_world_titles(gold_engine: Engine, *, pipeline_version: str) -> None:
    """Set every `dim_driver.world_titles` from how many `dim_season` rows name them `champion_driver_id`.

    Global (not scoped to one season) — a driver's title count only ever
    grows as more seasons are transformed, so this is always recomputed
    from every `dim_season` row currently in Gold, not just the season
    `run_transform` was invoked for.

    Counts by `champion_driver_id` (a FK into `dim_driver`), not by the
    `champion_driver` display-name string — two drivers sharing an
    identical full name, or a later name correction, would otherwise
    silently misattribute a championship count to the wrong driver (Phase
    7 audit, Critical). Seasons transformed before this ID column existed
    have `champion_driver_id IS NULL` and are simply excluded until
    re-transformed, rather than falling back to the unsafe name match.
    """
    dim_season = reflect_table(
        gold_engine,
        "dim_season",
        Column("season_id", Uuid(), primary_key=True),
        Column("champion_driver_id", Uuid()),
    )
    dim_driver = reflect_table(
        gold_engine,
        "dim_driver",
        Column("driver_id", Uuid(), primary_key=True),
        Column("team_id", Uuid()),
    )

    with gold_engine.connect() as connection:
        champion_ids = [
            row[0]
            for row in connection.execute(
                select(dim_season.c.champion_driver_id).where(
                    dim_season.c.champion_driver_id.is_not(None)
                )
            )
        ]
        title_counts: dict[Any, int] = defaultdict(int)
        for driver_id in champion_ids:
            title_counts[driver_id] += 1

        driver_rows = connection.execute(select(dim_driver.c.driver_id)).all()
        for (driver_id,) in driver_rows:
            connection.execute(
                dim_driver.update()
                .where(dim_driver.c.driver_id == driver_id)
                .values(world_titles=title_counts.get(driver_id, 0), updated_at=func.now())
            )
        connection.commit()


# ---------------------------------------------------------------------------
# Marts: dim_*/fct_* -> mart_* (aggregation on top of Gold, never Bronze)
# ---------------------------------------------------------------------------


def _is_dnf(status: str | None) -> bool:
    """Best-effort retirement detection.

    FastF1 and Jolpica both use `"Finished"` for a classified finisher, and
    either a `"+N Lap(s)"` prefix or the literal `"Lapped"` for a
    lapped-but-still-classified finisher (confirmed against real 2024
    Bahrain GP data, where both sources report `"Lapped"` rather than
    `"+1 Lap"`) — anything else (`"Retired"`, `"Accident"`, `"Engine"`,
    `"DNS"`, `"Disqualified"`, ...) is treated as a DNF. There is no
    structured status taxonomy in this pipeline's data to do better than
    this string check; a `None` status (no result recorded at all) is not
    counted as a DNF, since that's a missing record, not an observed
    retirement.
    """
    if status is None:
        return False
    return not (status == "Finished" or status == "Lapped" or status.startswith("+"))


@dataclass(frozen=True, slots=True)
class _MartContext:
    """Every Gold row this season's four marts need, loaded once and shared.

    All four marts overlap heavily in which `dim_*`/`fct_*` rows they read
    (`fct_results`/`fct_laps`/`fct_pitstop`, driver/constructor names,
    session metadata) — loading them once here rather than once per mart
    avoids four nearly-identical round trips to the Gold database.
    `results`/`laps` carry two extra keys not present in the underlying
    table (`_driver_team_id`, `_session_type`), added here specifically so
    each mart function can filter/group without re-joining `dim_driver`/
    `dim_session` itself.
    """

    season_id: uuid.UUID
    sessions: list[dict[str, Any]]
    results: list[dict[str, Any]]
    laps: list[dict[str, Any]]
    pitstops: list[dict[str, Any]]
    driver_names: dict[uuid.UUID, str]
    constructor_names: dict[uuid.UUID, str]
    weather_rainfall_by_id: dict[uuid.UUID, bool | None]


def _load_mart_context(gold_engine: Engine, season: int) -> _MartContext:
    season_id = generate_id("gold_season", str(season))
    dim_session = reflect_table(
        gold_engine,
        "dim_session",
        Column("session_id", Uuid(), primary_key=True),
        Column("season_id", Uuid()),
        Column("weather_id", Uuid()),
        Column("circuit_id", Uuid()),
    )
    dim_driver = reflect_table(
        gold_engine,
        "dim_driver",
        Column("driver_id", Uuid(), primary_key=True),
        Column("team_id", Uuid()),
    )
    dim_constructor = reflect_table(
        gold_engine, "dim_constructor", Column("constructor_id", Uuid(), primary_key=True)
    )
    dim_weather = reflect_table(
        gold_engine, "dim_weather", Column("weather_id", Uuid(), primary_key=True)
    )
    fct_result = reflect_table(
        gold_engine,
        "fct_results",
        Column("result_id", Uuid(), primary_key=True),
        Column("driver_id", Uuid()),
        Column("session_id", Uuid()),
    )
    fct_lap = reflect_table(
        gold_engine,
        "fct_laps",
        Column("lap_id", Uuid(), primary_key=True),
        Column("driver_id", Uuid()),
        Column("session_id", Uuid()),
    )
    fct_pitstop = reflect_table(
        gold_engine,
        "fct_pitstop",
        Column("pitstop_id", Uuid(), primary_key=True),
        Column("driver_id", Uuid()),
        Column("session_id", Uuid()),
    )

    with gold_engine.connect() as connection:
        sessions = [
            dict(row)
            for row in connection.execute(
                select(dim_session).where(dim_session.c.season_id == season_id)
            ).mappings()
        ]
        session_ids = [session["session_id"] for session in sessions]

        driver_rows = connection.execute(
            select(dim_driver.c.driver_id, dim_driver.c.full_name, dim_driver.c.team_id)
        ).all()
        driver_names = {row.driver_id: row.full_name for row in driver_rows}
        driver_team_by_id = {row.driver_id: row.team_id for row in driver_rows}

        constructor_names = {
            row.constructor_id: row.team_name
            for row in connection.execute(
                select(dim_constructor.c.constructor_id, dim_constructor.c.team_name)
            )
        }
        weather_rainfall_by_id = {
            row.weather_id: row.rainfall
            for row in connection.execute(select(dim_weather.c.weather_id, dim_weather.c.rainfall))
        }

        results: list[dict[str, Any]] = []
        laps: list[dict[str, Any]] = []
        pitstops: list[dict[str, Any]] = []
        if session_ids:
            results = [
                dict(row)
                for row in connection.execute(
                    select(fct_result).where(fct_result.c.session_id.in_(session_ids))
                ).mappings()
            ]
            laps = [
                dict(row)
                for row in connection.execute(
                    select(fct_lap).where(fct_lap.c.session_id.in_(session_ids))
                ).mappings()
            ]
            pitstops = [
                dict(row)
                for row in connection.execute(
                    select(fct_pitstop).where(fct_pitstop.c.session_id.in_(session_ids))
                ).mappings()
            ]

    session_type_by_id = {session["session_id"]: session["session_type"] for session in sessions}
    for result in results:
        result["_driver_team_id"] = driver_team_by_id.get(result["driver_id"])
        result["_session_type"] = session_type_by_id.get(result["session_id"])
    for lap in laps:
        lap["_session_type"] = session_type_by_id.get(lap["session_id"])

    return _MartContext(
        season_id=season_id,
        sessions=sessions,
        results=results,
        laps=laps,
        pitstops=pitstops,
        driver_names=driver_names,
        constructor_names=constructor_names,
        weather_rainfall_by_id=weather_rainfall_by_id,
    )


def _transform_mart_driver_summary(
    gold_engine: Engine, context: _MartContext, *, pipeline_version: str
) -> int:
    """Upsert one `mart_driver_summary` row per driver with at least one result this season.

    `poles` prefers actual Qualifying-session results (`finish_position ==
    1` in a `session_type="Q"` `fct_results` row) when any exist for this
    driver; otherwise it falls back to counting race `grid_position == 1`
    as a proxy, since a driver's starting grid slot is usually — but not
    always, given grid penalties — their qualifying position.
    `consistency_score` is `None` on fewer than two race results, since a
    standard deviation over a single value is meaningless; otherwise it's
    `100 - population_stdev(finish_positions) * 10`, clamped at `0` — an
    ad hoc but monotonic scale (tighter finishing positions score higher)
    docs/07_DATABASE_SCHEMA.md doesn't itself define a formula for.
    `race_pace`/`qualifying_pace`/`pit_efficiency` exclude in/out laps and
    average the rest directly in seconds — lower is better for all three.
    """
    race_results_by_driver: dict[uuid.UUID, list[dict[str, Any]]] = defaultdict(list)
    quali_results_by_driver: dict[uuid.UUID, list[dict[str, Any]]] = defaultdict(list)
    for result in context.results:
        if result["_session_type"] == "R":
            race_results_by_driver[result["driver_id"]].append(result)
        elif result["_session_type"] == "Q":
            quali_results_by_driver[result["driver_id"]].append(result)

    race_laps_by_driver: dict[uuid.UUID, list[float]] = defaultdict(list)
    quali_laps_by_driver: dict[uuid.UUID, list[float]] = defaultdict(list)
    for lap in context.laps:
        if lap["lap_time"] is None or lap["pit_in"] or lap["pit_out"]:
            continue
        if lap["_session_type"] == "R":
            race_laps_by_driver[lap["driver_id"]].append(lap["lap_time"])
        elif lap["_session_type"] == "Q":
            quali_laps_by_driver[lap["driver_id"]].append(lap["lap_time"])

    pit_durations_by_driver: dict[uuid.UUID, list[float]] = defaultdict(list)
    for stop in context.pitstops:
        if stop["pit_duration"] is not None:
            pit_durations_by_driver[stop["driver_id"]].append(stop["pit_duration"])

    driver_ids = {result["driver_id"] for result in context.results}
    rows = []
    for driver_id in driver_ids:
        race_results = race_results_by_driver.get(driver_id, [])
        finishes = [r["finish_position"] for r in race_results if r["finish_position"] is not None]
        grids = [r["grid_position"] for r in race_results if r["grid_position"] is not None]
        quali_finishes = [
            r["finish_position"]
            for r in quali_results_by_driver.get(driver_id, [])
            if r["finish_position"] is not None
        ]

        average_qualifying: float | None
        if quali_finishes:
            poles = sum(1 for position in quali_finishes if position == 1)
            average_qualifying = statistics.fmean(quali_finishes)
        else:
            poles = sum(1 for position in grids if position == 1)
            average_qualifying = statistics.fmean(grids) if grids else None

        consistency_score = None
        if len(finishes) >= 2:
            consistency_score = max(0.0, 100.0 - statistics.pstdev(finishes) * 10)

        pit_durations = pit_durations_by_driver.get(driver_id, [])
        race_pace_laps = race_laps_by_driver.get(driver_id, [])
        quali_pace_laps = quali_laps_by_driver.get(driver_id, [])

        rows.append(
            {
                "mart_driver_summary_id": generate_id(
                    "mart_driver_summary", f"{context.season_id}:{driver_id}"
                ),
                "source": _TRANSFORM_SOURCE,
                "pipeline_version": pipeline_version,
                "season_id": context.season_id,
                "driver_id": driver_id,
                "driver": context.driver_names.get(driver_id, "Unknown"),
                "wins": sum(1 for position in finishes if position == 1),
                "podiums": sum(1 for position in finishes if position <= 3),
                "poles": poles,
                "fastest_laps": sum(1 for result in race_results if result["fastest_lap"]),
                "average_finish": statistics.fmean(finishes) if finishes else None,
                "average_qualifying": average_qualifying,
                "consistency_score": consistency_score,
                "pit_efficiency": statistics.fmean(pit_durations) if pit_durations else None,
                "race_pace": statistics.fmean(race_pace_laps) if race_pace_laps else None,
                "qualifying_pace": statistics.fmean(quali_pace_laps) if quali_pace_laps else None,
            }
        )

    table = reflect_table(
        gold_engine,
        "mart_driver_summary",
        Column("mart_driver_summary_id", Uuid(), primary_key=True),
        Column("season_id", Uuid()),
        Column("driver_id", Uuid()),
    )
    return upsert(gold_engine, table, rows, conflict_columns=["season_id", "driver_id"])


def _transform_mart_constructor_summary(
    gold_engine: Engine, context: _MartContext, *, pipeline_version: str
) -> int:
    """Upsert one `mart_constructor_summary` row per constructor with at least one race result this season.

    Every stat aggregates across *all* of a constructor's drivers'
    results/laps/stops this season, resolved via `dim_driver.team_id`
    (see `_transform_drivers` for how that FK gets resolved in the first
    place). `strategy_success`/`development_index` have no source in this
    pipeline — see `app/models/gold/mart_constructor_summary.py`.
    """
    driver_team_by_id = {
        result["driver_id"]: result["_driver_team_id"] for result in context.results
    }

    race_results_by_constructor: dict[uuid.UUID, list[dict[str, Any]]] = defaultdict(list)
    for result in context.results:
        if result["_session_type"] != "R" or result["_driver_team_id"] is None:
            continue
        race_results_by_constructor[result["_driver_team_id"]].append(result)

    race_laps_by_constructor: dict[uuid.UUID, list[float]] = defaultdict(list)
    for lap in context.laps:
        if lap["_session_type"] != "R" or lap["lap_time"] is None or lap["pit_in"] or lap["pit_out"]:
            continue
        team_id = driver_team_by_id.get(lap["driver_id"])
        if team_id is not None:
            race_laps_by_constructor[team_id].append(lap["lap_time"])

    pit_durations_by_constructor: dict[uuid.UUID, list[float]] = defaultdict(list)
    for stop in context.pitstops:
        if stop["pit_duration"] is None:
            continue
        team_id = driver_team_by_id.get(stop["driver_id"])
        if team_id is not None:
            pit_durations_by_constructor[team_id].append(stop["pit_duration"])

    rows = []
    for constructor_id, results in race_results_by_constructor.items():
        finishes = [r["finish_position"] for r in results if r["finish_position"] is not None]
        points = [r["points"] for r in results if r["points"] is not None]
        statuses = [r["status"] for r in results]
        pit_durations = pit_durations_by_constructor.get(constructor_id, [])
        race_pace_laps = race_laps_by_constructor.get(constructor_id, [])
        dnf_count = sum(1 for status in statuses if _is_dnf(status))

        rows.append(
            {
                "mart_constructor_summary_id": generate_id(
                    "mart_constructor_summary", f"{context.season_id}:{constructor_id}"
                ),
                "source": _TRANSFORM_SOURCE,
                "pipeline_version": pipeline_version,
                "season_id": context.season_id,
                "constructor_id": constructor_id,
                "constructor": context.constructor_names.get(constructor_id, "Unknown"),
                "wins": sum(1 for position in finishes if position == 1),
                "podiums": sum(1 for position in finishes if position <= 3),
                "pitstop_average": statistics.fmean(pit_durations) if pit_durations else None,
                "strategy_success": None,
                "average_points": statistics.fmean(points) if points else None,
                "dnf_rate": (dnf_count / len(statuses)) if statuses else None,
                "development_index": None,
                "average_pace": statistics.fmean(race_pace_laps) if race_pace_laps else None,
            }
        )

    table = reflect_table(
        gold_engine,
        "mart_constructor_summary",
        Column("mart_constructor_summary_id", Uuid(), primary_key=True),
        Column("season_id", Uuid()),
        Column("constructor_id", Uuid()),
    )
    return upsert(gold_engine, table, rows, conflict_columns=["season_id", "constructor_id"])


def _transform_mart_race_summary(
    gold_engine: Engine, context: _MartContext, *, pipeline_version: str
) -> int:
    """Upsert one `mart_race_summary` row per `session_type="R"` session this season.

    `pole` is a best-effort proxy (`grid_position == 1`), same caveat as
    `mart_driver_summary.poles`. `weather` is a short display label
    (`"Wet"`/`"Dry"`/`None`) derived from the session's linked
    `dim_weather.rainfall`, not the full weather record — see
    `app/models/gold/mart_race_summary.py`. `safety_car_laps`/`red_flags`
    have no source in this pipeline.
    """
    results_by_session: dict[uuid.UUID, list[dict[str, Any]]] = defaultdict(list)
    for result in context.results:
        results_by_session[result["session_id"]].append(result)

    pitstops_by_session: dict[uuid.UUID, list[dict[str, Any]]] = defaultdict(list)
    for stop in context.pitstops:
        pitstops_by_session[stop["session_id"]].append(stop)

    rows = []
    for session in context.sessions:
        if session["session_type"] != "R":
            continue
        session_id = session["session_id"]
        results = results_by_session.get(session_id, [])
        winner = next((r for r in results if r["finish_position"] == 1), None)
        pole = next((r for r in results if r["grid_position"] == 1), None)
        fastest = next((r for r in results if r["fastest_lap"]), None)
        pit_durations = [
            stop["pit_duration"]
            for stop in pitstops_by_session.get(session_id, [])
            if stop["pit_duration"] is not None
        ]
        retirements = sum(1 for result in results if _is_dnf(result["status"]))

        weather_id = session["weather_id"]
        rainfall = context.weather_rainfall_by_id.get(weather_id) if weather_id else None
        weather_label = None if rainfall is None else ("Wet" if rainfall else "Dry")

        rows.append(
            {
                "session_id": session_id,
                "source": _TRANSFORM_SOURCE,
                "pipeline_version": pipeline_version,
                "race": session["race_name"],
                "winner": context.driver_names.get(winner["driver_id"]) if winner else None,
                "pole": context.driver_names.get(pole["driver_id"]) if pole else None,
                "fastest_lap": context.driver_names.get(fastest["driver_id"]) if fastest else None,
                "average_pitstop": statistics.fmean(pit_durations) if pit_durations else None,
                "safety_car_laps": None,
                "red_flags": None,
                "weather": weather_label,
                "retirements": retirements,
            }
        )

    table = reflect_table(
        gold_engine, "mart_race_summary", Column("session_id", Uuid(), primary_key=True)
    )
    return upsert(gold_engine, table, rows, conflict_columns=["session_id"])


def _average_overtakes_per_race(context: _MartContext) -> float | None:
    """Approximates on-track overtakes per race for `mart_dashboard.average_overtakes`.

    For each race session, counts how many times any driver's `position`
    improved from their own previous recorded lap, then averages that
    count across every race session this season. A genuine overtake
    improves exactly one driver's position and worsens exactly one
    other's — counting only improvements (never regressions) means each
    real overtake is counted exactly once, from the overtaking driver's
    side, with no double-counting. This is an approximation, not an exact
    count: it can't distinguish a genuine on-track pass from a position
    gained through pit strategy or another driver's retirement, since no
    race-control event data exists in this pipeline to disambiguate.
    Returns `None` if this season has no race sessions with lap position
    data at all, rather than a misleading `0`.
    """
    laps_by_session_and_driver: dict[tuple[uuid.UUID, uuid.UUID], list[dict[str, Any]]] = (
        defaultdict(list)
    )
    for lap in context.laps:
        if lap["_session_type"] != "R" or lap["position"] is None:
            continue
        laps_by_session_and_driver[(lap["session_id"], lap["driver_id"])].append(lap)

    overtakes_by_session: dict[uuid.UUID, int] = defaultdict(int)
    for (session_id, _driver_id), laps in laps_by_session_and_driver.items():
        ordered = sorted(laps, key=lambda lap: lap["lap_number"])
        for previous, current in itertools.pairwise(ordered):
            if current["position"] < previous["position"]:
                overtakes_by_session[session_id] += 1

    race_session_ids = {
        session["session_id"] for session in context.sessions if session["session_type"] == "R"
    }
    if not race_session_ids:
        return None
    counts = [overtakes_by_session.get(session_id, 0) for session_id in race_session_ids]
    return statistics.fmean(counts)


def _transform_mart_dashboard(
    gold_engine: Engine, context: _MartContext, season: int, *, pipeline_version: str
) -> int:
    """Upsert `mart_dashboard`'s single row for this season.

    `championship_gap` is the points gap between the top two drivers by
    total race points scored so far *this season* — independent of, and
    computed the same way as, `_finalize_season_champion`'s own
    (separate) query, since that function only needs the single leader,
    not the runner-up.
    """
    dim_season = reflect_table(
        gold_engine, "dim_season", Column("season_id", Uuid(), primary_key=True)
    )
    with gold_engine.connect() as connection:
        season_row = connection.execute(
            select(dim_season).where(dim_season.c.season_id == context.season_id)
        ).mappings().one()

    race_results = [result for result in context.results if result["_session_type"] == "R"]
    driver_ids = {result["driver_id"] for result in race_results}
    constructor_ids = {
        result["_driver_team_id"] for result in race_results if result["_driver_team_id"] is not None
    }

    pit_durations = [
        stop["pit_duration"] for stop in context.pitstops if stop["pit_duration"] is not None
    ]
    fastest_pitstop = min(pit_durations) if pit_durations else None

    race_laps = [
        lap for lap in context.laps if lap["_session_type"] == "R" and lap["lap_time"] is not None
    ]
    fastest_lap_time = None
    fastest_lap_driver = None
    if race_laps:
        fastest = min(race_laps, key=lambda lap: lap["lap_time"])
        fastest_lap_time = fastest["lap_time"]
        fastest_lap_driver = context.driver_names.get(fastest["driver_id"])

    points_by_driver: dict[uuid.UUID, float] = defaultdict(float)
    for result in race_results:
        if result["points"] is not None:
            points_by_driver[result["driver_id"]] += result["points"]
    standings = sorted(points_by_driver.values(), reverse=True)
    championship_gap = (standings[0] - standings[1]) if len(standings) >= 2 else None

    row = {
        "season_id": context.season_id,
        "source": _TRANSFORM_SOURCE,
        "pipeline_version": pipeline_version,
        "season": season,
        "drivers": len(driver_ids),
        "constructors": len(constructor_ids),
        "races": season_row["race_count"],
        "fastest_pitstop": fastest_pitstop,
        "average_overtakes": _average_overtakes_per_race(context),
        "fastest_lap_time": fastest_lap_time,
        "fastest_lap_driver": fastest_lap_driver,
        "championship_gap": championship_gap,
    }
    table = reflect_table(gold_engine, "mart_dashboard", Column("season_id", Uuid(), primary_key=True))
    return upsert(gold_engine, table, [row], conflict_columns=["season_id"])


def _transform_marts(gold_engine: Engine, season: int, *, pipeline_version: str) -> dict[str, int]:
    """Builds every mart for this season from Gold's own dimensions/facts.

    Never reads Bronze — marts are a pure aggregation on top of whatever
    `_transform_*` already produced earlier in this same `run_transform`
    call. One shared `_MartContext` is loaded once (see that class) and
    reused across all four marts.
    """
    context = _load_mart_context(gold_engine, season)
    return {
        "mart_driver_summary": _transform_mart_driver_summary(
            gold_engine, context, pipeline_version=pipeline_version
        ),
        "mart_constructor_summary": _transform_mart_constructor_summary(
            gold_engine, context, pipeline_version=pipeline_version
        ),
        "mart_race_summary": _transform_mart_race_summary(
            gold_engine, context, pipeline_version=pipeline_version
        ),
        "mart_dashboard": _transform_mart_dashboard(
            gold_engine, context, season, pipeline_version=pipeline_version
        ),
    }


def run_transform(raw_engine: Engine, gold_engine: Engine, *, season: int, pipeline_version: str) -> dict[str, int]:
    """Transform one season's Bronze data into Gold, in the only order that's correct.

    Order, and why it can't be reshuffled:

    1. Circuits, constructors, drivers (global dimensions — drivers'
       `team_id` resolution reads `dim_constructor`, so constructors must
       exist first).
    2. This season's `dim_season` shell (`race_count`/`sprint_count` only
       — `dim_session` below needs `season_id` to exist as a foreign key
       target).
    3. This season's `dim_weather` (aggregated per session — `dim_session`
       below needs `weather_id` to exist as a foreign key target).
    4. This season's `dim_session` (needs season/weather/circuit
       dimensions from steps 1-3).
    5. This season's `fct_laps` (needs `dim_driver`/`dim_session`) —
       returns per-driver-per-session lap groups that steps 6 and 7 both
       reuse rather than re-querying Bronze.
    6. This season's `fct_pitstop`, derived from step 5's lap groups.
    7. This season's `fct_results`, reconciling FastF1/Jolpica and using
       step 5's lap groups for `fastest_lap`/`laps_completed`.
    8. Finalize `dim_season.champion_driver`/`champion_constructor` from
       this run's own `fct_results` (step 7 must exist first).
    9. Finalize every `dim_driver.world_titles` from every `dim_season`
       row now in Gold (global, not just this season — step 8 must exist
       first for *this* season to be reflected, but earlier seasons'
       championships, if already transformed, count too).
    10. Build every `mart_*` for this season (steps 1-9 must all be
        complete first — marts aggregate from the dimensions/facts those
        steps just finished writing, never from Bronze).

    Returns a dict of `{step_name: rows_upserted}` for logging.

    Each of the 10 steps above commits its own independent transaction (via
    `utils.db.upsert`) — there is no outer transaction wrapping all of
    them. If a later step raises, earlier steps stay committed, leaving
    Gold partially updated for this season with nothing else telling an
    operator that happened (Phase 7 audit, High: "a blind re-run isn't the
    only way this gets noticed"). This function is idempotent and safe to
    re-run, but the `except` block below logs exactly which step failed and
    which steps already committed, so that fact doesn't depend on someone
    reading this docstring first.
    """
    summary: dict[str, int] = {}
    current_step = "circuits"
    try:
        summary["circuits"] = _transform_circuits(
            raw_engine, gold_engine, pipeline_version=pipeline_version
        )
        current_step = "constructors"
        summary["constructors"] = _transform_constructors(
            raw_engine, gold_engine, pipeline_version=pipeline_version
        )
        current_step = "drivers"
        summary["drivers"] = _transform_drivers(
            raw_engine, gold_engine, pipeline_version=pipeline_version
        )
        current_step = "season"
        summary["season"] = _transform_season_shell(
            raw_engine, gold_engine, season, pipeline_version=pipeline_version
        )
        current_step = "weather"
        summary["weather"] = _transform_weather(
            raw_engine, gold_engine, season, pipeline_version=pipeline_version
        )
        current_step = "sessions"
        summary["sessions"] = _transform_sessions(
            raw_engine, gold_engine, season, pipeline_version=pipeline_version
        )
        current_step = "laps"
        laps_count, laps_by_driver_session = _transform_laps(
            raw_engine, gold_engine, season, pipeline_version=pipeline_version
        )
        summary["laps"] = laps_count
        current_step = "pitstops"
        summary["pitstops"] = _transform_pitstops(
            gold_engine, season, laps_by_driver_session, pipeline_version=pipeline_version
        )
        current_step = "results"
        summary["results"] = _transform_results(
            raw_engine, gold_engine, season, laps_by_driver_session, pipeline_version=pipeline_version
        )
        current_step = "finalize_season_champion"
        _finalize_season_champion(gold_engine, season, pipeline_version=pipeline_version)
        current_step = "finalize_driver_world_titles"
        _finalize_driver_world_titles(gold_engine, pipeline_version=pipeline_version)
        current_step = "marts"
        summary.update(_transform_marts(gold_engine, season, pipeline_version=pipeline_version))
    except Exception:
        logger.exception(
            "run_transform failed at step %r for season %s; steps already committed for this "
            "season (%s) are left in place, and Gold is now partially updated until a re-run "
            "completes successfully",
            current_step,
            season,
            ", ".join(summary) or "none",
        )
        raise
    return summary
