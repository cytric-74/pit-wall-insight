"""Business logic behind `/constructors*` (docs/08_API_SPECIFICATION.md — "Constructors")."""

from __future__ import annotations

import statistics
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import NotFoundError
from app.models import DimConstructor, MartConstructorSummary
from app.repositories import constructor_repository
from app.schemas.compare import ConstructorComparison, ConstructorComparisonEntry
from app.schemas.constructor import (
    Constructor,
    ConstructorCareerStatistics,
    ConstructorSeasonSummary,
)
from app.schemas.driver import Driver


def _mean(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return statistics.fmean(present) if present else None


def _constructor_from_model(model: DimConstructor) -> Constructor:
    return Constructor(
        id=model.constructor_id,
        team_name=model.team_name,
        base_country=model.base_country,
        active=model.active,
    )


async def _get_constructor_or_404(session: AsyncSession, constructor_id: uuid.UUID) -> Constructor:
    model = await constructor_repository.get_constructor_by_id(session, constructor_id)
    if model is None:
        raise NotFoundError(f"Constructor {constructor_id} not found.")
    return _constructor_from_model(model)


async def list_constructors(
    session: AsyncSession, *, page: int, limit: int
) -> tuple[list[Constructor], int]:
    models, total = await constructor_repository.list_constructors(session, page=page, limit=limit)
    return [_constructor_from_model(model) for model in models], total


async def get_constructor(session: AsyncSession, constructor_id: uuid.UUID) -> Constructor:
    return await _get_constructor_or_404(session, constructor_id)


async def get_current_drivers(session: AsyncSession, constructor_id: uuid.UUID) -> list[Driver]:
    constructor = await _get_constructor_or_404(session, constructor_id)
    drivers = await constructor_repository.list_current_drivers(session, constructor_id)
    return [
        Driver(
            id=driver.driver_id,
            driver_number=driver.driver_number,
            full_name=driver.full_name,
            abbreviation=driver.abbreviation,
            nationality=driver.nationality,
            date_of_birth=driver.date_of_birth,
            team_id=driver.team_id,
            team=constructor.team_name,
            rookie_season=driver.rookie_season,
            world_titles=driver.world_titles,
            active=driver.active,
        )
        for driver in drivers
    ]


def _season_summary(row: object) -> ConstructorSeasonSummary:
    summary = row.MartConstructorSummary  # type: ignore[attr-defined]
    return ConstructorSeasonSummary(
        season=row.season,  # type: ignore[attr-defined]
        wins=summary.wins,
        podiums=summary.podiums,
        pitstop_average=summary.pitstop_average,
        strategy_success=summary.strategy_success,
        average_points=summary.average_points,
        dnf_rate=summary.dnf_rate,
        development_index=summary.development_index,
        average_pace=summary.average_pace,
    )


async def get_performance_trend(
    session: AsyncSession, constructor_id: uuid.UUID
) -> list[ConstructorSeasonSummary]:
    await _get_constructor_or_404(session, constructor_id)
    rows = await constructor_repository.list_season_summaries_for_constructor(
        session, constructor_id
    )
    return [_season_summary(row) for row in rows]


async def get_career_statistics(
    session: AsyncSession, constructor_id: uuid.UUID
) -> ConstructorCareerStatistics:
    constructor = await _get_constructor_or_404(session, constructor_id)
    rows = await constructor_repository.list_season_summaries_for_constructor(
        session, constructor_id
    )
    summaries = [row.MartConstructorSummary for row in rows]

    return ConstructorCareerStatistics(
        constructor=constructor.team_name,
        seasons_competed=len(summaries),
        wins=sum(summary.wins for summary in summaries),
        podiums=sum(summary.podiums for summary in summaries),
        average_points=_mean([summary.average_points for summary in summaries]),
        dnf_rate=_mean([summary.dnf_rate for summary in summaries]),
    )


def _comparison_entry(name: str, summary: MartConstructorSummary) -> ConstructorComparisonEntry:
    return ConstructorComparisonEntry(
        constructor=name,
        wins=summary.wins,
        podiums=summary.podiums,
        pitstop_average=summary.pitstop_average,
        strategy_success=summary.strategy_success,
        average_points=summary.average_points,
        dnf_rate=summary.dnf_rate,
        development_index=summary.development_index,
        average_pace=summary.average_pace,
    )


async def compare_constructors(
    session: AsyncSession,
    constructor_a_id: uuid.UUID,
    constructor_b_id: uuid.UUID,
    *,
    season: int | None,
) -> ConstructorComparison:
    constructor_a = await _get_constructor_or_404(session, constructor_a_id)
    constructor_b = await _get_constructor_or_404(session, constructor_b_id)

    rows_a = await constructor_repository.list_season_summaries_for_constructor(
        session, constructor_a_id
    )
    rows_b = await constructor_repository.list_season_summaries_for_constructor(
        session, constructor_b_id
    )
    summaries_a = {row.season: row.MartConstructorSummary for row in rows_a}
    summaries_b = {row.season: row.MartConstructorSummary for row in rows_b}

    if season is not None:
        resolved_season = season
    else:
        common_seasons = set(summaries_a) & set(summaries_b)
        if not common_seasons:
            raise NotFoundError(
                f"No season with data for both "
                f"{constructor_a.team_name} and {constructor_b.team_name}."
            )
        resolved_season = max(common_seasons)

    if resolved_season not in summaries_a or resolved_season not in summaries_b:
        raise NotFoundError(
            f"Season {resolved_season} has no data for both "
            f"{constructor_a.team_name} and {constructor_b.team_name}."
        )

    return ConstructorComparison(
        season=resolved_season,
        constructor_a=_comparison_entry(constructor_a.team_name, summaries_a[resolved_season]),
        constructor_b=_comparison_entry(constructor_b.team_name, summaries_b[resolved_season]),
    )
