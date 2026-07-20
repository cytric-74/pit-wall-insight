"""`/races*` (docs/08_API_SPECIFICATION.md — "Races")."""

from __future__ import annotations

import math
import uuid

from fastapi import APIRouter, Query, Request

from app.dependencies.database import AnalyticsDbSession
from app.schemas.common import CollectionResponse, Pagination, SuccessResponse
from app.schemas.race import (
    DriverStrategy,
    PitstopEntry,
    PositionEntry,
    RaceListItem,
    RaceSummary,
    RaceWeather,
)
from app.services import race_service
from app.utils.responses import build_meta

router = APIRouter(prefix="/races", tags=["Races"])


@router.get("", response_model=CollectionResponse[RaceListItem], summary="Race list")
async def list_races(
    db: AnalyticsDbSession,
    season: int | None = Query(None),
    country: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
) -> CollectionResponse[RaceListItem]:
    items, total = await race_service.list_races(
        db, season=season, country=country, page=page, limit=limit
    )
    pages = math.ceil(total / limit) if limit else 0
    return CollectionResponse(
        data=items, pagination=Pagination(page=page, limit=limit, total=total, pages=pages)
    )


@router.get("/{race_id}", response_model=SuccessResponse[RaceSummary], summary="Race summary")
async def get_race(
    race_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[RaceSummary]:
    data = await race_service.get_race(db, race_id)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{race_id}/positions",
    response_model=SuccessResponse[list[PositionEntry]],
    summary="Position changes",
)
async def get_race_positions(
    race_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[list[PositionEntry]]:
    data = await race_service.get_positions(db, race_id)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{race_id}/pitstops",
    response_model=SuccessResponse[list[PitstopEntry]],
    summary="Pit stop timeline",
)
async def get_race_pitstops(
    race_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[list[PitstopEntry]]:
    data = await race_service.get_pitstops(db, race_id)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{race_id}/weather", response_model=SuccessResponse[RaceWeather], summary="Weather snapshot"
)
async def get_race_weather(
    race_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[RaceWeather]:
    data = await race_service.get_weather(db, race_id)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{race_id}/strategy",
    response_model=SuccessResponse[list[DriverStrategy]],
    summary="Strategy overview",
)
async def get_race_strategy(
    race_id: uuid.UUID, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[list[DriverStrategy]]:
    data = await race_service.get_strategy(db, race_id)
    return SuccessResponse(data=data, meta=build_meta(request))
