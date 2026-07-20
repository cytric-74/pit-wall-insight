"""Read-only Gold-layer queries backing `/constructors*` (docs/08_API_SPECIFICATION.md)."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Row, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DimConstructor, DimDriver, DimSeason, MartConstructorSummary


async def list_constructors(
    session: AsyncSession, *, page: int, limit: int
) -> tuple[list[DimConstructor], int]:
    total = (
        await session.execute(select(func.count()).select_from(DimConstructor))
    ).scalar_one()
    result = await session.execute(
        select(DimConstructor)
        .order_by(DimConstructor.team_name)
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return list(result.scalars().all()), total


async def get_constructor_by_id(
    session: AsyncSession, constructor_id: uuid.UUID
) -> DimConstructor | None:
    result = await session.execute(
        select(DimConstructor).where(DimConstructor.constructor_id == constructor_id)
    )
    return result.scalar_one_or_none()


async def list_current_drivers(
    session: AsyncSession, constructor_id: uuid.UUID
) -> list[DimDriver]:
    result = await session.execute(
        select(DimDriver)
        .where(DimDriver.team_id == constructor_id, DimDriver.active.is_(True))
        .order_by(DimDriver.full_name)
    )
    return list(result.scalars().all())


async def list_season_summaries_for_constructor(
    session: AsyncSession, constructor_id: uuid.UUID
) -> list[Row[Any]]:
    """Every `mart_constructor_summary` row for this constructor, oldest season first."""
    statement = (
        select(DimSeason.year.label("season"), MartConstructorSummary)
        .join(DimSeason, DimSeason.season_id == MartConstructorSummary.season_id)
        .where(MartConstructorSummary.constructor_id == constructor_id)
        .order_by(DimSeason.year)
    )
    result = await session.execute(statement)
    return list(result.all())
