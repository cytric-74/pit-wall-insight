"""`/seasons*` (docs/08_API_SPECIFICATION.md — "Seasons")."""

from __future__ import annotations

from fastapi import APIRouter, Query, Request

from app.dependencies.database import AnalyticsDbSession
from app.schemas.common import CollectionResponse, SuccessResponse
from app.schemas.season import CalendarEntry, SeasonListItem, SeasonSummary, StandingsData
from app.services import season_service
from app.utils.responses import build_meta, build_pagination

router = APIRouter(prefix="/seasons", tags=["Seasons"])


@router.get("", response_model=CollectionResponse[SeasonListItem], summary="Available seasons")
async def list_seasons(
    db: AnalyticsDbSession,
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
) -> CollectionResponse[SeasonListItem]:
    items, total = await season_service.list_seasons(db, page=page, limit=limit)
    return CollectionResponse(data=items, pagination=build_pagination(total, page, limit))


@router.get("/{year}", response_model=SuccessResponse[SeasonSummary], summary="Season summary")
async def get_season_summary(
    year: int, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[SeasonSummary]:
    data = await season_service.get_season_summary(db, year)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{year}/standings",
    response_model=SuccessResponse[StandingsData],
    summary="Championship standings",
)
async def get_standings(
    year: int, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[StandingsData]:
    data = await season_service.get_standings(db, year)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/{year}/calendar",
    response_model=SuccessResponse[list[CalendarEntry]],
    summary="Race calendar",
)
async def get_calendar(
    year: int, request: Request, db: AnalyticsDbSession
) -> SuccessResponse[list[CalendarEntry]]:
    data = await season_service.get_calendar(db, year)
    return SuccessResponse(data=data, meta=build_meta(request))
