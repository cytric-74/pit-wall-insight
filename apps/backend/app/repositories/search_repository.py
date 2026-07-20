"""Read-only Gold-layer queries backing `/search` (docs/08_API_SPECIFICATION.md).

Substring matching via `func.lower(column).like(...)` rather than `ILIKE`
— `ILIKE` is Postgres-only, and this project's tests run against SQLite
(no Postgres in this environment); `lower()` + `like()` behaves the same
on both dialects.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import Row, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DimCircuit, DimConstructor, DimDriver, DimSeason, DimSession

_RACE_SESSION_TYPE = "R"
_DEFAULT_LIMIT = 10


def _pattern(query: str) -> str:
    return f"%{query.lower()}%"


async def search_drivers(
    session: AsyncSession, query: str, *, limit: int = _DEFAULT_LIMIT
) -> list[DimDriver]:
    result = await session.execute(
        select(DimDriver)
        .where(func.lower(DimDriver.full_name).like(_pattern(query)))
        .order_by(DimDriver.full_name)
        .limit(limit)
    )
    return list(result.scalars().all())


async def search_constructors(
    session: AsyncSession, query: str, *, limit: int = _DEFAULT_LIMIT
) -> list[DimConstructor]:
    result = await session.execute(
        select(DimConstructor)
        .where(func.lower(DimConstructor.team_name).like(_pattern(query)))
        .order_by(DimConstructor.team_name)
        .limit(limit)
    )
    return list(result.scalars().all())


async def search_circuits(
    session: AsyncSession, query: str, *, limit: int = _DEFAULT_LIMIT
) -> list[DimCircuit]:
    result = await session.execute(
        select(DimCircuit)
        .where(func.lower(DimCircuit.name).like(_pattern(query)))
        .order_by(DimCircuit.name)
        .limit(limit)
    )
    return list(result.scalars().all())


async def search_races(
    session: AsyncSession, query: str, *, limit: int = _DEFAULT_LIMIT
) -> list[Row[Any]]:
    statement = (
        select(DimSession.session_id, DimSession.race_name, DimSeason.year)
        .join(DimSeason, DimSeason.season_id == DimSession.season_id)
        .where(
            DimSession.session_type == _RACE_SESSION_TYPE,
            func.lower(DimSession.race_name).like(_pattern(query)),
        )
        .order_by(DimSeason.year.desc())
        .limit(limit)
    )
    result = await session.execute(statement)
    return list(result.all())


async def search_seasons(
    session: AsyncSession, query: str, *, limit: int = _DEFAULT_LIMIT
) -> list[DimSeason]:
    result = await session.execute(
        select(DimSeason)
        .where(func.lower(func.cast(DimSeason.year, String)).like(_pattern(query)))
        .order_by(DimSeason.year.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
