"""Business logic behind `/strategy/tyres` (docs/08_API_SPECIFICATION.md — "Strategy")."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import strategy_repository
from app.schemas.strategy import TyreDegradation, TyreDegradationPoint


async def get_tyre_degradation(
    session: AsyncSession,
    *,
    season: int | None,
    driver_id: uuid.UUID | None,
    round_number: int | None,
    session_type: str | None,
) -> TyreDegradation:
    rows = await strategy_repository.get_tyre_degradation(
        session,
        season=season,
        driver_id=driver_id,
        round_number=round_number,
        session_type=session_type,
    )
    return TyreDegradation(
        points=[
            TyreDegradationPoint(
                compound=row.compound,
                tyre_life=row.tyre_life,
                average_lap_time=row.average_lap_time,
                sample_count=row.sample_count,
            )
            for row in rows
        ]
    )
