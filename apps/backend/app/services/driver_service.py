"""Business logic behind `/drivers*` (docs/08_API_SPECIFICATION.md — "Drivers").

Career-wide rollups (`get_career_statistics`, `get_consistency`) sum/average
across `mart_driver_summary` rows in Python rather than via a repository
aggregate query — that table is already one small row per season per
driver, so there's no meaningful query-optimization benefit to pushing the
rollup into SQL, and it keeps `driver_repository` limited to "fetch rows"
the way `app/repositories/README` (docs/05_BACKEND_ARCHITECTURE.md) expects.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from typing import Any

from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MartDriverSummary
from app.repositories import driver_repository
from app.schemas.driver import (
    Driver,
    DriverCareerStatistics,
    DriverComparison,
    DriverComparisonEntry,
    DriverConsistency,
    DriverLap,
    SeasonConsistencyEntry,
)
from app.services.common import get_or_404, mean, resolve_comparison_season

_VALID_SORT_FIELDS = {"full_name", "driver_number"}
_DEFAULT_SORT = "full_name"


@dataclass(frozen=True, slots=True)
class _DriverRow:
    """The shape `driver_repository.get_driver_by_id`/`list_drivers` return.

    Built once, here, from the untyped `Row[Any]` both repository
    functions return — every field read off the row happens in this one
    place instead of scattered across `_driver_from_row` with a
    `# type: ignore[attr-defined]` per field (Phase 7 audit, Medium); a
    typo below would be mypy-strict-checked same as any other dataclass
    field, whereas a typo in a bare `row.attr` access silently passing
    unchecked was exactly the risk that carried.
    """

    driver_id: uuid.UUID
    driver_number: int | None
    full_name: str
    abbreviation: str | None
    nationality: str | None
    date_of_birth: date | None
    team_id: uuid.UUID | None
    team: str | None
    rookie_season: int | None
    world_titles: int | None
    active: bool | None


def _driver_from_row(row: Row[Any]) -> Driver:
    typed = _DriverRow(
        driver_id=row.driver_id,
        driver_number=row.driver_number,
        full_name=row.full_name,
        abbreviation=row.abbreviation,
        nationality=row.nationality,
        date_of_birth=row.date_of_birth,
        team_id=row.team_id,
        team=row.team,
        rookie_season=row.rookie_season,
        world_titles=row.world_titles,
        active=row.active,
    )
    return Driver(
        id=typed.driver_id,
        driver_number=typed.driver_number,
        full_name=typed.full_name,
        abbreviation=typed.abbreviation,
        nationality=typed.nationality,
        date_of_birth=typed.date_of_birth,
        team_id=typed.team_id,
        team=typed.team,
        rookie_season=typed.rookie_season,
        world_titles=typed.world_titles,
        active=typed.active,
    )


async def _get_driver_or_404(session: AsyncSession, driver_id: uuid.UUID) -> Driver:
    row = await get_or_404(
        driver_repository.get_driver_by_id(session, driver_id), f"Driver {driver_id} not found."
    )
    return _driver_from_row(row)


async def list_drivers(
    session: AsyncSession,
    *,
    season: int | None,
    constructor_id: uuid.UUID | None,
    nationality: str | None,
    active: bool | None,
    sort: str,
    page: int,
    limit: int,
) -> tuple[list[Driver], int]:
    resolved_sort = sort if sort in _VALID_SORT_FIELDS else _DEFAULT_SORT
    rows, total = await driver_repository.list_drivers(
        session,
        season=season,
        constructor_id=constructor_id,
        nationality=nationality,
        active=active,
        sort=resolved_sort,
        page=page,
        limit=limit,
    )
    return [_driver_from_row(row) for row in rows], total


async def get_driver(session: AsyncSession, driver_id: uuid.UUID) -> Driver:
    return await _get_driver_or_404(session, driver_id)


async def get_career_statistics(
    session: AsyncSession, driver_id: uuid.UUID
) -> DriverCareerStatistics:
    driver = await _get_driver_or_404(session, driver_id)
    rows = await driver_repository.list_season_summaries_for_driver(session, driver_id)
    summaries = [row.MartDriverSummary for row in rows]

    return DriverCareerStatistics(
        driver=driver.full_name,
        seasons_competed=len(summaries),
        wins=sum(summary.wins for summary in summaries),
        podiums=sum(summary.podiums for summary in summaries),
        poles=sum(summary.poles for summary in summaries),
        fastest_laps=sum(summary.fastest_laps for summary in summaries),
        average_finish=mean([summary.average_finish for summary in summaries]),
        consistency_score=mean([summary.consistency_score for summary in summaries]),
    )


async def get_laps(
    session: AsyncSession,
    driver_id: uuid.UUID,
    *,
    season: int | None,
    round_number: int | None,
    session_type: str | None,
    compound: str | None,
) -> list[DriverLap]:
    await _get_driver_or_404(session, driver_id)
    rows = await driver_repository.list_laps_for_driver(
        session,
        driver_id,
        season=season,
        round_number=round_number,
        session_type=session_type,
        compound=compound,
    )
    return [
        DriverLap(
            season=row.season,
            round=row.round,
            race_name=row.race_name,
            session_type=row.session_type,
            lap_number=row.lap_number,
            lap_time=row.lap_time,
            sector_1=row.sector_1,
            sector_2=row.sector_2,
            sector_3=row.sector_3,
            compound=row.compound,
            tyre_life=row.tyre_life,
            position=row.position,
            pit_in=row.pit_in,
            pit_out=row.pit_out,
        )
        for row in rows
    ]


async def get_consistency(session: AsyncSession, driver_id: uuid.UUID) -> DriverConsistency:
    driver = await _get_driver_or_404(session, driver_id)
    rows = await driver_repository.list_season_summaries_for_driver(session, driver_id)
    seasons = [
        SeasonConsistencyEntry(
            season=row.season,
            consistency_score=row.MartDriverSummary.consistency_score,
            average_finish=row.MartDriverSummary.average_finish,
        )
        for row in rows
    ]
    return DriverConsistency(
        driver=driver.full_name,
        career_consistency_score=mean([entry.consistency_score for entry in seasons]),
        seasons=seasons,
    )


def _comparison_entry(driver_name: str, summary: MartDriverSummary) -> DriverComparisonEntry:
    # `summary` is already a real, fully-typed `MartDriverSummary` ORM
    # instance (selecting the whole mapped class, not individual labeled
    # columns) — the parameter was previously widened to `object`, which
    # is what forced a `# type: ignore[attr-defined]` per field below even
    # though none was actually needed (Phase 7 audit, Medium).
    return DriverComparisonEntry(
        driver=driver_name,
        wins=summary.wins,
        podiums=summary.podiums,
        poles=summary.poles,
        fastest_laps=summary.fastest_laps,
        average_finish=summary.average_finish,
        average_qualifying=summary.average_qualifying,
        consistency_score=summary.consistency_score,
        pit_efficiency=summary.pit_efficiency,
        race_pace=summary.race_pace,
        qualifying_pace=summary.qualifying_pace,
    )


async def compare_drivers(
    session: AsyncSession,
    driver_a_id: uuid.UUID,
    driver_b_id: uuid.UUID,
    *,
    season: int | None,
) -> DriverComparison:
    driver_a = await _get_driver_or_404(session, driver_a_id)
    driver_b = await _get_driver_or_404(session, driver_b_id)

    rows_a = await driver_repository.list_season_summaries_for_driver(session, driver_a_id)
    rows_b = await driver_repository.list_season_summaries_for_driver(session, driver_b_id)
    summaries_a = {row.season: row.MartDriverSummary for row in rows_a}
    summaries_b = {row.season: row.MartDriverSummary for row in rows_b}

    resolved_season = resolve_comparison_season(
        summaries_a,
        summaries_b,
        season,
        entity_a_name=driver_a.full_name,
        entity_b_name=driver_b.full_name,
    )

    return DriverComparison(
        season=resolved_season,
        driver_a=_comparison_entry(driver_a.full_name, summaries_a[resolved_season]),
        driver_b=_comparison_entry(driver_b.full_name, summaries_b[resolved_season]),
    )
