"""Transforms one season's Bronze data into Gold dimensions and facts.

Purpose
-------
`run_transform` is the single public entrypoint: given a season, it reads
every relevant `raw_*` row from the Bronze database and upserts the
corresponding `dim_*`/`fct_*` rows into the Gold database, in a fixed
internal order (see that function's docstring for exactly why the order
matters).

This module used to hold every transform function inline (1,430 lines —
by a wide margin the largest file in the ingestion app), mixing three
distinct concerns that could never be approached in isolation (Phase 7
audit, Medium). It's now the thin orchestrator only: the `dim_*`/`fct_*`
transforms live in `transformers/dimensions.py`, the two post-hoc
"finalize" passes in `transformers/finalize.py`, and the four mart-
builders in `transformers/marts.py` — all three re-exported through
`run_transform` here, which remains the only thing that should call any
of them, and only in the order it enforces.
"""

from __future__ import annotations

import logging

from sqlalchemy.engine import Engine

from transformers.dimensions import (
    _transform_circuits,
    _transform_constructors,
    _transform_drivers,
    _transform_laps,
    _transform_pitstops,
    _transform_results,
    _transform_season_shell,
    _transform_sessions,
    _transform_weather,
)
from transformers.finalize import _finalize_driver_world_titles, _finalize_season_champion
from transformers.marts import _transform_marts

logger = logging.getLogger("ingestion.transformers")


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
