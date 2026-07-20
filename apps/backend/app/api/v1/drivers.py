"""`/drivers*` (docs/08_API_SPECIFICATION.md — "Drivers").

Path identifiers are Gold `driver_id` UUIDs (no human-readable slug exists
in this warehouse — see `app/models/gold/driver.py`).
"""

from __future__ import annotations

import math
import uuid

from fastapi import APIRouter, Query, Request

from app.dependencies.database import AnalyticsDbSession
from app.schemas.common import CollectionResponse, Pagination, SuccessResponse
from app.schemas.driver import (
    Driver,
    DriverCareerStatistics,
    DriverComparison,
    DriverConsistency,
    DriverLap,
)
from app.services import driver_service
from app.utils.responses import build_meta

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.get("", response_model=CollectionResponse[Driver], summary="Driver list")
async def list_drivers(
    db: AnalyticsDbSession,
    season: int | None = Query(None),
    constructor: uuid.UUID | None = Query(None),  # noqa: B008
    nationality: str | None = Query(None),
    active: bool | None = Query(None),
    sort: str = Query("full_name"),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
) -> CollectionResponse[Driver]:
    items, total = await driver_service.list_drivers(
        db,
        season=season,
        constructor_id=constructor,
        nationality=nationality,
        active=active,
        sort=sort,
        page=page,
        limit=limit,
    )
    pages = math.ceil(total / limit) if limit else 0
    return CollectionResponse(
        data=items, pagination=Pagination(page=page, limit=limit, total=total, pages=pages)
    )


@router.get("/{driver_id}", response_model=SuccessResponse[Driver], summary="Driver profile")
async def get_driver(
    driver_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[Driver]:
    data = await driver_service.get_driver(db, driver_id)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{driver_id}/statistics",
    response_model=SuccessResponse[DriverCareerStatistics],
    summary="Career statistics",
)
async def get_driver_statistics(
    driver_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[DriverCareerStatistics]:
    data = await driver_service.get_career_statistics(db, driver_id)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{driver_id}/laps", response_model=SuccessResponse[list[DriverLap]], summary="Lap data"
)
async def get_driver_laps(
    driver_id: uuid.UUID,
    request: Request,
    db: AnalyticsDbSession,
    season: int | None = Query(None),
    race: int | None = Query(None, description="Round number"),
    session: str | None = Query(None, description="Session type, e.g. R, Q, FP1"),
    compound: str | None = Query(None),
) -> SuccessResponse[list[DriverLap]]:
    data = await driver_service.get_laps(
        db, driver_id, season=season, round_number=race, session_type=session, compound=compound
    )
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{driver_id}/consistency",
    response_model=SuccessResponse[DriverConsistency],
    summary="Consistency metrics",
)
async def get_driver_consistency(
    driver_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[DriverConsistency]:
    data = await driver_service.get_consistency(db, driver_id)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{driver_id}/comparison/{other_driver_id}",
    response_model=SuccessResponse[DriverComparison],
    summary="Driver comparison",
)
async def compare_drivers(
    driver_id: uuid.UUID,
    other_driver_id: uuid.UUID,
    request: Request,
    db: AnalyticsDbSession,
    season: int | None = Query(None),
) -> SuccessResponse[DriverComparison]:
    data = await driver_service.compare_drivers(db, driver_id, other_driver_id, season=season)
    return SuccessResponse(data=data, meta=build_meta(request))
