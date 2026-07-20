"""Business logic behind `/drivers*` (docs/08_API_SPECIFICATION.md — "Drivers").

Career-wide rollups (`get_career_statistics`, `get_consistency`) sum/average
across `mart_driver_summary` rows in Python rather than via a repository
aggregate query — that table is already one small row per season per
driver, so there's no meaningful query-optimization benefit to pushing the
rollup into SQL, and it keeps `driver_repository` limited to "fetch rows"
the way `app/repositories/README` (docs/05_BACKEND_ARCHITECTURE.md) expects.
"""

from __future__ import annotations

import statistics
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import NotFoundError
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

_VALID_SORT_FIELDS = {"full_name", "driver_number"}
_DEFAULT_SORT = "full_name"


def _mean(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return statistics.fmean(present) if present else None


def _driver_from_row(row: object) -> Driver:
    return Driver(
        id=row.driver_id,  # type: ignore[attr-defined]
        driver_number=row.driver_number,  # type: ignore[attr-defined]
        full_name=row.full_name,  # type: ignore[attr-defined]
        abbreviation=row.abbreviation,  # type: ignore[attr-defined]
        nationality=row.nationality,  # type: ignore[attr-defined]
        date_of_birth=row.date_of_birth,  # type: ignore[attr-defined]
        team_id=row.team_id,  # type: ignore[attr-defined]
        team=row.team,  # type: ignore[attr-defined]
        rookie_season=row.rookie_season,  # type: ignore[attr-defined]
        world_titles=row.world_titles,  # type: ignore[attr-defined]
        active=row.active,  # type: ignore[attr-defined]
    )


async def _get_driver_or_404(session: AsyncSession, driver_id: uuid.UUID) -> Driver:
    row = await driver_repository.get_driver_by_id(session, driver_id)
    if row is None:
        raise NotFoundError(f"Driver {driver_id} not found.")
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
        average_finish=_mean([summary.average_finish for summary in summaries]),
        consistency_score=_mean([summary.consistency_score for summary in summaries]),
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
        career_consistency_score=_mean([entry.consistency_score for entry in seasons]),
        seasons=seasons,
    )


def _comparison_entry(driver_name: str, summary: object) -> DriverComparisonEntry:
    return DriverComparisonEntry(
        driver=driver_name,
        wins=summary.wins,  # type: ignore[attr-defined]
        podiums=summary.podiums,  # type: ignore[attr-defined]
        poles=summary.poles,  # type: ignore[attr-defined]
        fastest_laps=summary.fastest_laps,  # type: ignore[attr-defined]
        average_finish=summary.average_finish,  # type: ignore[attr-defined]
        average_qualifying=summary.average_qualifying,  # type: ignore[attr-defined]
        consistency_score=summary.consistency_score,  # type: ignore[attr-defined]
        pit_efficiency=summary.pit_efficiency,  # type: ignore[attr-defined]
        race_pace=summary.race_pace,  # type: ignore[attr-defined]
        qualifying_pace=summary.qualifying_pace,  # type: ignore[attr-defined]
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

    if season is not None:
        resolved_season = season
    else:
        common_seasons = set(summaries_a) & set(summaries_b)
        if not common_seasons:
            raise NotFoundError(
                f"No season with data for both {driver_a.full_name} and {driver_b.full_name}."
            )
        resolved_season = max(common_seasons)

    if resolved_season not in summaries_a or resolved_season not in summaries_b:
        raise NotFoundError(
            f"Season {resolved_season} has no data for both "
            f"{driver_a.full_name} and {driver_b.full_name}."
        )

    return DriverComparison(
        season=resolved_season,
        driver_a=_comparison_entry(driver_a.full_name, summaries_a[resolved_season]),
        driver_b=_comparison_entry(driver_b.full_name, summaries_b[resolved_season]),
    )
