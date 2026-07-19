"""Ingestion pipeline CLI.

Purpose
-------
A command-line entrypoint that runs the full collect -> validate -> load
pipeline for one season (and optionally one race): collects raw records
from FastF1 or Jolpica-F1, validates them, and — unless `--dry-run` is
given — upserts the valid ones into the raw/bronze database via
`loaders/bronze_loader.py`, printing a human-readable summary throughout.

`--dry-run` preserves this CLI's original Phase 1 behavior (collect and
validate only, print a summary, touch no database) — useful for checking
whether a season's data validates cleanly before committing to loading it
anywhere.

Usage
-----
    cd apps/ingestion
    python -m main --season 2024 --entities fastf1-schedule,jolpica-calendar
    python -m main --season 2024 --round 1 --entities fastf1-results,fastf1-laps
    python -m main --season 2024 --dry-run --entities jolpica-calendar

Run `python -m main --help` for the full list of available entities.

Inputs
------
Command-line arguments: `--season` (required), `--round` and `--session`
(required only for entities scoped to a single race), `--entities` (a
comma-separated subset of `ENTITY_HANDLERS`' keys), `--dry-run` (skip
loading), and `--database-url` (override `Settings.database_url`, e.g. to
point at a test database).

Outputs
-------
A process exit code (`0` if every requested entity collected and validated
without a collector-level failure; `1` if any entity was unknown or its
collector raised — individual record validation failures do *not* affect
the exit code, since docs/06_DATA_ENGINEERING.md is explicit that the
pipeline should continue past those). A structured log stream (via
`utils.logging.PipelineLogger`) plus a plain-text summary printed to
stdout for whoever is running the CLI interactively.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import cast

from pydantic import BaseModel
from sqlalchemy.engine import Engine

from collectors.ergast_client import (
    get_constructor_standings,
    get_driver_standings,
    get_race_results,
    get_season_calendar,
)
from collectors.exceptions import CollectorError
from collectors.fastf1_client import (
    get_event_schedule,
    get_session_laps,
    get_session_results,
    get_session_weather,
)
from config.settings import get_settings
from loaders import bronze_loader
from utils.logging import PipelineLogger
from validators.schema import (
    RawConstructorStanding,
    RawDriverStanding,
    RawEventSchedule,
    RawRaceCalendarEntry,
    RawRaceResult,
    RawSessionLap,
    RawSessionResult,
    RawWeatherSample,
)
from validators.validate import ValidationResult, validate_records

logger = logging.getLogger("ingestion.main")


@dataclass(frozen=True, slots=True)
class Args:
    """Parsed CLI arguments, typed so the rest of this module never touches `argparse.Namespace` directly."""

    season: int
    round: int | None
    session: str
    entities: list[str]
    dry_run: bool
    database_url: str | None


@dataclass(frozen=True, slots=True)
class CollectedBatch:
    """What one entity handler produced, ready to hand to `validate_records`.

    `model` is the Pydantic model (from `validators/schema.py`) that
    describes this batch's expected shape — carried alongside the raw
    records themselves so `run()` never has to maintain its own separate
    "which model goes with which entity" lookup.
    """

    source: str
    model: type[BaseModel]
    raw_records: list[dict[str, object]]
    natural_key_field: str | None


def _require_round(args: Args, entity_name: str) -> int:
    """Fetch `args.round`, raising a clear error if the caller omitted it.

    Several entities (anything scoped to one race rather than a whole
    season) need `--round`; rather than let a missing round surface as a
    confusing `TypeError` deep inside a collector call, this fails fast
    with a message naming exactly which entity needed it.
    """
    if args.round is None:
        raise SystemExit(f"--round is required for entity {entity_name!r}")
    return args.round


# ---------------------------------------------------------------------------
# Collectors: raw -> validated records
# ---------------------------------------------------------------------------


def _collect_fastf1_schedule(args: Args) -> CollectedBatch:
    records = get_event_schedule(args.season)
    return CollectedBatch("fastf1", RawEventSchedule, records, "RoundNumber")


def _collect_fastf1_results(args: Args) -> CollectedBatch:
    round_number = _require_round(args, "fastf1-results")
    records = get_session_results(args.season, round_number, args.session)
    return CollectedBatch("fastf1", RawSessionResult, records, "DriverNumber")


def _collect_fastf1_laps(args: Args) -> CollectedBatch:
    round_number = _require_round(args, "fastf1-laps")
    records = get_session_laps(args.season, round_number, args.session)
    return CollectedBatch("fastf1", RawSessionLap, records, "Driver")


def _collect_fastf1_weather(args: Args) -> CollectedBatch:
    round_number = _require_round(args, "fastf1-weather")
    records = get_session_weather(args.season, round_number, args.session)
    return CollectedBatch("fastf1", RawWeatherSample, records, "Time")


def _collect_jolpica_calendar(args: Args) -> CollectedBatch:
    records = get_season_calendar(args.season)
    return CollectedBatch("jolpica", RawRaceCalendarEntry, records, "round")


def _collect_jolpica_driver_standings(args: Args) -> CollectedBatch:
    records = get_driver_standings(args.season)
    # No `natural_key_field`: the driver id lives at `record["Driver"]["driverId"]`,
    # a nested path `validate_records` doesn't attempt to resolve — a minor
    # debug-log convenience isn't worth adding nested-path lookup logic for.
    return CollectedBatch("jolpica", RawDriverStanding, records, None)


def _collect_jolpica_constructor_standings(args: Args) -> CollectedBatch:
    records = get_constructor_standings(args.season)
    return CollectedBatch("jolpica", RawConstructorStanding, records, None)


def _collect_jolpica_race_results(args: Args) -> CollectedBatch:
    round_number = _require_round(args, "jolpica-race-results")
    records = get_race_results(args.season, round_number)
    return CollectedBatch("jolpica", RawRaceResult, records, "number")


ENTITY_HANDLERS: dict[str, Callable[[Args], CollectedBatch]] = {
    "fastf1-schedule": _collect_fastf1_schedule,
    "fastf1-results": _collect_fastf1_results,
    "fastf1-laps": _collect_fastf1_laps,
    "fastf1-weather": _collect_fastf1_weather,
    "jolpica-calendar": _collect_jolpica_calendar,
    "jolpica-driver-standings": _collect_jolpica_driver_standings,
    "jolpica-constructor-standings": _collect_jolpica_constructor_standings,
    "jolpica-race-results": _collect_jolpica_race_results,
}


# ---------------------------------------------------------------------------
# Loaders: validated records -> raw/bronze database
# ---------------------------------------------------------------------------
# One function per entity, each returning the total row count upserted
# across every table it touches. Several entities write to more than one
# table (e.g. a race result also tells us about a driver and a
# constructor) — that fan-out lives here, one level above
# `bronze_loader`'s single-table upsert functions, so each of those stays
# focused on exactly one table.


def _load_fastf1_schedule(
    engine: Engine, records: list[BaseModel], args: Args, pipeline_version: str
) -> int:
    return bronze_loader.upsert_sessions_from_schedule(
        engine, cast(list[RawEventSchedule], records), pipeline_version=pipeline_version
    )


def _load_fastf1_results(
    engine: Engine, records: list[BaseModel], args: Args, pipeline_version: str
) -> int:
    round_number = _require_round(args, "fastf1-results")
    return bronze_loader.upsert_results_fastf1(
        engine,
        cast(list[RawSessionResult], records),
        season=args.season,
        round_number=round_number,
        session_type=args.session,
        pipeline_version=pipeline_version,
    )


def _load_fastf1_laps(
    engine: Engine, records: list[BaseModel], args: Args, pipeline_version: str
) -> int:
    round_number = _require_round(args, "fastf1-laps")
    return bronze_loader.upsert_laps(
        engine,
        cast(list[RawSessionLap], records),
        season=args.season,
        round_number=round_number,
        session_type=args.session,
        pipeline_version=pipeline_version,
    )


def _load_fastf1_weather(
    engine: Engine, records: list[BaseModel], args: Args, pipeline_version: str
) -> int:
    round_number = _require_round(args, "fastf1-weather")
    return bronze_loader.upsert_weather(
        engine,
        cast(list[RawWeatherSample], records),
        season=args.season,
        round_number=round_number,
        session_type=args.session,
        pipeline_version=pipeline_version,
    )


def _load_jolpica_calendar(
    engine: Engine, records: list[BaseModel], args: Args, pipeline_version: str
) -> int:
    calendar = cast(list[RawRaceCalendarEntry], records)
    sessions = bronze_loader.upsert_sessions_from_calendar(
        engine, calendar, pipeline_version=pipeline_version
    )
    circuits = bronze_loader.upsert_circuits_from_calendar(
        engine, calendar, pipeline_version=pipeline_version
    )
    return sessions + circuits


def _load_jolpica_driver_standings(
    engine: Engine, records: list[BaseModel], args: Args, pipeline_version: str
) -> int:
    standings = cast(list[RawDriverStanding], records)
    drivers = bronze_loader.upsert_drivers(
        engine, (standing.Driver for standing in standings), pipeline_version=pipeline_version
    )
    constructors = bronze_loader.upsert_constructors(
        engine,
        (constructor for standing in standings for constructor in standing.Constructors),
        pipeline_version=pipeline_version,
    )
    return drivers + constructors


def _load_jolpica_constructor_standings(
    engine: Engine, records: list[BaseModel], args: Args, pipeline_version: str
) -> int:
    standings = cast(list[RawConstructorStanding], records)
    return bronze_loader.upsert_constructors(
        engine,
        (standing.Constructor for standing in standings),
        pipeline_version=pipeline_version,
    )


def _load_jolpica_race_results(
    engine: Engine, records: list[BaseModel], args: Args, pipeline_version: str
) -> int:
    round_number = _require_round(args, "jolpica-race-results")
    results = cast(list[RawRaceResult], records)
    result_count = bronze_loader.upsert_results_jolpica(
        engine,
        results,
        season=args.season,
        round_number=round_number,
        pipeline_version=pipeline_version,
    )
    drivers = bronze_loader.upsert_drivers(
        engine, (result.Driver for result in results), pipeline_version=pipeline_version
    )
    constructors = bronze_loader.upsert_constructors(
        engine, (result.Constructor for result in results), pipeline_version=pipeline_version
    )
    return result_count + drivers + constructors


ENTITY_LOADERS: dict[str, Callable[[Engine, list[BaseModel], Args, str], int]] = {
    "fastf1-schedule": _load_fastf1_schedule,
    "fastf1-results": _load_fastf1_results,
    "fastf1-laps": _load_fastf1_laps,
    "fastf1-weather": _load_fastf1_weather,
    "jolpica-calendar": _load_jolpica_calendar,
    "jolpica-driver-standings": _load_jolpica_driver_standings,
    "jolpica-constructor-standings": _load_jolpica_constructor_standings,
    "jolpica-race-results": _load_jolpica_race_results,
}


def parse_args(argv: Sequence[str] | None = None) -> Args:
    """Parse and validate command-line arguments.

    Inputs: `argv` — argument list, or `None` to read from `sys.argv`
    (the `None` default is what makes this function callable identically
    from both `if __name__ == "__main__"` and from tests).

    Outputs: a typed `Args` instance.

    Edge case: `--entities` is split and stripped here so callers never see
    empty strings from trailing commas or accidental whitespace (e.g.
    `"fastf1-schedule, jolpica-calendar"` with a space after the comma).
    """
    parser = argparse.ArgumentParser(
        description="Collect, validate, and load Formula One data from FastF1 and Jolpica-F1."
    )
    parser.add_argument("--season", type=int, required=True, help="Season year, e.g. 2024.")
    parser.add_argument(
        "--round",
        type=int,
        default=None,
        help="Round number, required for entities scoped to a single race "
        "(fastf1-results, fastf1-laps, fastf1-weather, jolpica-race-results).",
    )
    parser.add_argument(
        "--session",
        default="R",
        help="FastF1 session identifier for fastf1-results/-laps/-weather "
        "(FP1/FP2/FP3/Q/S/SQ/R). Defaults to 'R' (Race).",
    )
    parser.add_argument(
        "--entities",
        default="fastf1-schedule,jolpica-calendar",
        help=f"Comma-separated entities to collect. Available: {', '.join(ENTITY_HANDLERS)}.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Collect and validate only; skip loading into the raw/bronze database.",
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="Override the raw/bronze database URL (defaults to Settings.database_url).",
    )
    parsed = parser.parse_args(argv)
    entities = [name.strip() for name in parsed.entities.split(",") if name.strip()]
    return Args(
        season=parsed.season,
        round=parsed.round,
        session=parsed.session,
        entities=entities,
        dry_run=parsed.dry_run,
        database_url=parsed.database_url,
    )


def _print_summary(entity_name: str, result: ValidationResult, *, sample_size: int = 5) -> None:
    """Print a human-readable summary of one entity's validation outcome to stdout.

    Distinct from `PipelineLogger`'s structured log output: this is for a
    person running the CLI interactively, not for a log aggregator, so it
    prints directly to stdout rather than through `logging`. Only the first
    `sample_size` issues are shown in full, to keep the output readable when
    a whole batch fails for the same reason (e.g. an upstream schema
    change) rather than printing hundreds of near-identical error blocks.
    """
    print(f"\n{entity_name}: {result.valid_count} valid, {result.issue_count} rejected")
    for issue in result.issues[:sample_size]:
        print(f"  - record #{issue.index} (natural_key={issue.natural_key!r}): {issue.errors}")
    remaining = result.issue_count - sample_size
    if remaining > 0:
        print(f"  ... and {remaining} more (see logs for the full list)")


def run(args: Args) -> int:
    """Run the collect -> validate -> load pipeline for every requested entity.

    Returns `0` if every entity was recognized and its collector call
    succeeded; `1` otherwise. A collector failure for one entity does not
    stop the remaining entities from being attempted — each is independent,
    the same "continue past a failure where possible" philosophy the
    validators apply at the record level, applied here at the entity level.

    The database engine (when not `--dry-run`) is created once and reused
    across every entity in this run, then disposed at the end — one
    connection pool per invocation, not one per entity.
    """
    settings = get_settings()
    run_id = f"{args.season}-{int(time.time())}"
    pipeline_logger = PipelineLogger(run_id=run_id)
    pipeline_logger.event(
        "Pipeline start", season=args.season, entities=",".join(args.entities), dry_run=args.dry_run
    )

    engine: Engine | None = None
    if not args.dry_run:
        engine = bronze_loader.create_bronze_engine(args.database_url or settings.database_url)

    exit_code = 0
    try:
        for entity_name in args.entities:
            handler = ENTITY_HANDLERS.get(entity_name)
            if handler is None:
                logger.error(
                    "Unknown entity %r; available: %s", entity_name, ", ".join(ENTITY_HANDLERS)
                )
                exit_code = 1
                continue

            try:
                with pipeline_logger.stage(f"collect:{entity_name}"):
                    batch = handler(args)
            except CollectorError as exc:
                logger.error("Collection failed for %s: %s", entity_name, exc)
                exit_code = 1
                continue

            with pipeline_logger.stage(f"validate:{entity_name}"):
                result = validate_records(
                    batch.model,
                    batch.raw_records,
                    source=batch.source,
                    entity=entity_name,
                    natural_key_field=batch.natural_key_field,
                )

            pipeline_logger.event(
                f"{entity_name} validated", valid=result.valid_count, issues=result.issue_count
            )
            _print_summary(entity_name, result)

            if engine is not None:
                loader = ENTITY_LOADERS[entity_name]
                with pipeline_logger.stage(f"load:{entity_name}"):
                    loaded = loader(engine, result.valid, args, settings.pipeline_version)
                pipeline_logger.event(f"{entity_name} loaded", rows=loaded)
                print(f"  loaded {loaded} row(s) into the raw/bronze database")
    finally:
        if engine is not None:
            engine.dispose()

    pipeline_logger.event("Pipeline end", exit_code=exit_code)
    return exit_code


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint: parse arguments and run the pipeline."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
