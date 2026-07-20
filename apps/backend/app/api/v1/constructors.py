"""`/constructors*` (docs/08_API_SPECIFICATION.md — "Constructors")."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, Request

from app.dependencies.database import AnalyticsDbSession
from app.schemas.common import CollectionResponse, SuccessResponse
from app.schemas.constructor import (
    Constructor,
    ConstructorCareerStatistics,
    ConstructorSeasonSummary,
)
from app.schemas.driver import Driver
from app.services import constructor_service
from app.utils.responses import build_meta, build_pagination

router = APIRouter(prefix="/constructors", tags=["Constructors"])


@router.get("", response_model=CollectionResponse[Constructor], summary="Constructor list")
async def list_constructors(
    db: AnalyticsDbSession,
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
) -> CollectionResponse[Constructor]:
    items, total = await constructor_service.list_constructors(db, page=page, limit=limit)
    return CollectionResponse(data=items, pagination=build_pagination(total, page, limit))


@router.get(
    "/{constructor_id}", response_model=SuccessResponse[Constructor], summary="Constructor profile"
)
async def get_constructor(
    constructor_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[Constructor]:
    data = await constructor_service.get_constructor(db, constructor_id)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{constructor_id}/drivers",
    response_model=SuccessResponse[list[Driver]],
    summary="Current drivers",
)
async def get_constructor_drivers(
    constructor_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[list[Driver]]:
    data = await constructor_service.get_current_drivers(db, constructor_id)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{constructor_id}/statistics",
    response_model=SuccessResponse[ConstructorCareerStatistics],
    summary="Team analytics",
)
async def get_constructor_statistics(
    constructor_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[ConstructorCareerStatistics]:
    data = await constructor_service.get_career_statistics(db, constructor_id)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{constructor_id}/performance",
    response_model=SuccessResponse[list[ConstructorSeasonSummary]],
    summary="Performance trends",
)
async def get_constructor_performance(
    constructor_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[list[ConstructorSeasonSummary]]:
    data = await constructor_service.get_performance_trend(db, constructor_id)
    return SuccessResponse(data=data, meta=build_meta(request))
