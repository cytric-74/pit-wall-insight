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

import uuid
from collections import defaultdict
from datetime import date
from typing import Any

from sqlalchemy import Column, Uuid, func, or_, select
from sqlalchemy.engine import Engine

from utils.db import reflect_table, upsert
from utils.ids import generate_id

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

        gold_rows: list[dict[str, Any]] = []
        for driver in driver_rows:
            natural_key = driver["driver_id"]
            code = driver["code"]

            conditions = [raw_results.c.driver_ref == natural_key]
            if code:
                conditions.append(raw_results.c.driver_code == code)
            matches = connection.execute(
                select(raw_results).where(or_(*conditions))
            ).mappings().all()

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
                constructor_row = connection.execute(
                    select(raw_constructors.c.id).where(
                        raw_constructors.c.constructor_id == constructor_ref
                    )
                ).first()
                if constructor_row is not None:
                    team_id = constructor_row[0]
            elif fastf1_candidates:
                constructor_ref = fastf1_candidates[-1]["constructor_ref"]
                constructor_row = connection.execute(
                    select(raw_constructors.c.id).where(
                        raw_constructors.c.name == constructor_ref
                    )
                ).first()
                if constructor_row is not None:
                    team_id = constructor_row[0]

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
    dim_season = reflect_table(gold_engine, "dim_season", Column("season_id", Uuid(), primary_key=True))

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
                champion_constructor=champion_constructor,
                updated_at=func.now(),
            )
        )
        connection.commit()


def _finalize_driver_world_titles(gold_engine: Engine, *, pipeline_version: str) -> None:
    """Set every `dim_driver.world_titles` from how many `dim_season` rows name them `champion_driver`.

    Global (not scoped to one season) — a driver's title count only ever
    grows as more seasons are transformed, so this is always recomputed
    from every `dim_season` row currently in Gold, not just the season
    `run_transform` was invoked for.
    """
    dim_season = reflect_table(gold_engine, "dim_season", Column("season_id", Uuid(), primary_key=True))
    dim_driver = reflect_table(
        gold_engine,
        "dim_driver",
        Column("driver_id", Uuid(), primary_key=True),
        Column("team_id", Uuid()),
    )

    with gold_engine.connect() as connection:
        champions = [
            row[0]
            for row in connection.execute(
                select(dim_season.c.champion_driver).where(dim_season.c.champion_driver.is_not(None))
            )
        ]
        title_counts: dict[str, int] = defaultdict(int)
        for name in champions:
            title_counts[name] += 1

        driver_rows = connection.execute(select(dim_driver.c.driver_id, dim_driver.c.full_name)).all()
        for driver_id, full_name in driver_rows:
            connection.execute(
                dim_driver.update()
                .where(dim_driver.c.driver_id == driver_id)
                .values(world_titles=title_counts.get(full_name, 0), updated_at=func.now())
            )
        connection.commit()


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

    Returns a dict of `{step_name: rows_upserted}` for logging.
    """
    summary: dict[str, int] = {}
    summary["circuits"] = _transform_circuits(raw_engine, gold_engine, pipeline_version=pipeline_version)
    summary["constructors"] = _transform_constructors(
        raw_engine, gold_engine, pipeline_version=pipeline_version
    )
    summary["drivers"] = _transform_drivers(raw_engine, gold_engine, pipeline_version=pipeline_version)
    summary["season"] = _transform_season_shell(
        raw_engine, gold_engine, season, pipeline_version=pipeline_version
    )
    summary["weather"] = _transform_weather(
        raw_engine, gold_engine, season, pipeline_version=pipeline_version
    )
    summary["sessions"] = _transform_sessions(
        raw_engine, gold_engine, season, pipeline_version=pipeline_version
    )
    laps_count, laps_by_driver_session = _transform_laps(
        raw_engine, gold_engine, season, pipeline_version=pipeline_version
    )
    summary["laps"] = laps_count
    summary["pitstops"] = _transform_pitstops(
        gold_engine, season, laps_by_driver_session, pipeline_version=pipeline_version
    )
    summary["results"] = _transform_results(
        raw_engine, gold_engine, season, laps_by_driver_session, pipeline_version=pipeline_version
    )
    _finalize_season_champion(gold_engine, season, pipeline_version=pipeline_version)
    _finalize_driver_world_titles(gold_engine, pipeline_version=pipeline_version)
    return summary
