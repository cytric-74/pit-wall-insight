"""Post-hoc "finalize" passes that run after every `dim_*`/`fct_*` transform for a season.

Purpose
-------
Both functions here set Gold columns that depend on data spanning more
than the season `run_transform` was invoked for — a season's champion
depends on that season's own `fct_results` (only meaningful once the
season is otherwise fully transformed), and a driver's world-title count
depends on *every* `dim_season` row currently in Gold. Split out of a
single 1,430-line `bronze_to_gold.py` (Phase 7 audit, Medium) alongside
`transformers/dimensions.py` (the `dim_*`/`fct_*` transforms) and
`transformers/marts.py` (the four mart-builders) — re-exported through
`run_transform` (`transformers/bronze_to_gold.py`), which is the only
thing that should call these directly, and only in the order it already
enforces.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy import Column, Uuid, func, select
from sqlalchemy.engine import Engine

from utils.db import reflect_table
from utils.ids import generate_id


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
