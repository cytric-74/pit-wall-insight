"""Gold `mart_*` builders — aggregation on top of `dim_*`/`fct_*`, never Bronze.

Purpose
-------
`_transform_marts` is the entrypoint `run_transform`
(`transformers/bronze_to_gold.py`) calls: it loads one shared
`_MartContext` (every Gold row this season's four marts need, fetched
once) and builds all four marts from it. None of this reads Bronze —
marts are a pure aggregation on top of whatever `transformers.dimensions`
already wrote earlier in the same `run_transform` call. Split out of a
single 1,430-line `bronze_to_gold.py` (Phase 7 audit, Medium) alongside
`transformers/dimensions.py` (the `dim_*`/`fct_*` transforms) and
`transformers/finalize.py` (the two post-hoc "finalize" passes).
"""

from __future__ import annotations

import itertools
import statistics
import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Column, Uuid, select
from sqlalchemy.engine import Engine

from utils.db import reflect_table, upsert
from utils.ids import generate_id

_TRANSFORM_SOURCE = "transform"


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
    (see `transformers.dimensions._transform_drivers` for how that FK gets
    resolved in the first place). `strategy_success`/`development_index`
    have no source in this pipeline — see
    `app/models/gold/mart_constructor_summary.py`.
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
    computed the same way as,
    `transformers.finalize._finalize_season_champion`'s own (separate)
    query, since that function only needs the single leader, not the
    runner-up.
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
    `transformers.dimensions` already produced earlier in this same
    `run_transform` call. One shared `_MartContext` is loaded once (see
    that class) and reused across all four marts.
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
