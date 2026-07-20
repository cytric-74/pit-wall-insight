"""`/strategy/tyres` (docs/08_API_SPECIFICATION.md — "Strategy")."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, Request

from app.dependencies.database import AnalyticsDbSession
from app.schemas.common import SuccessResponse
from app.schemas.strategy import TyreDegradation
from app.services import strategy_service
from app.utils.responses import build_meta

router = APIRouter(prefix="/strategy", tags=["Strategy"])


@router.get(
    "/tyres", response_model=SuccessResponse[TyreDegradation], summary="Tyre degradation"
)
async def get_tyre_degradation(
    request: Request,
    db: AnalyticsDbSession,
    season: int | None = Query(None),
    driver: uuid.UUID | None = Query(None),  # noqa: B008
    race: int | None = Query(None, description="Round number"),
    session: str | None = Query("R", description="Session type, e.g. R, Q, FP1"),
) -> SuccessResponse[TyreDegradation]:
    data = await strategy_service.get_tyre_degradation(
        db, season=season, driver_id=driver, round_number=race, session_type=session
    )
    return SuccessResponse(data=data, meta=build_meta(request))
