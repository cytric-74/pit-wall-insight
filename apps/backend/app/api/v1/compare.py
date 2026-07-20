"""`/compare/*` (docs/08_API_SPECIFICATION.md — "Comparison")."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, Request

from app.dependencies.database import AnalyticsDbSession
from app.schemas.common import SuccessResponse
from app.schemas.compare import ConstructorComparison, RaceComparison
from app.schemas.driver import DriverComparison
from app.services import compare_service, constructor_service, driver_service
from app.utils.responses import build_meta

router = APIRouter(prefix="/compare", tags=["Comparison"])


@router.get(
    "/drivers", response_model=SuccessResponse[DriverComparison], summary="Driver comparison"
)
async def compare_drivers(
    request: Request,
    db: AnalyticsDbSession,
    driver_a: uuid.UUID = Query(..., alias="driverA"),  # noqa: B008
    driver_b: uuid.UUID = Query(..., alias="driverB"),  # noqa: B008
    season: int | None = Query(None),
) -> SuccessResponse[DriverComparison]:
    data = await driver_service.compare_drivers(db, driver_a, driver_b, season=season)
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get(
    "/constructors",
    response_model=SuccessResponse[ConstructorComparison],
    summary="Constructor comparison",
)
async def compare_constructors(
    request: Request,
    db: AnalyticsDbSession,
    constructor_a: uuid.UUID = Query(..., alias="constructorA"),  # noqa: B008
    constructor_b: uuid.UUID = Query(..., alias="constructorB"),  # noqa: B008
    season: int | None = Query(None),
) -> SuccessResponse[ConstructorComparison]:
    data = await constructor_service.compare_constructors(
        db, constructor_a, constructor_b, season=season
    )
    return SuccessResponse(data=data, meta=build_meta(request))


@router.get("/races", response_model=SuccessResponse[RaceComparison], summary="Race comparison")
async def compare_races(
    request: Request,
    db: AnalyticsDbSession,
    race_a: uuid.UUID = Query(..., alias="raceA"),  # noqa: B008
    race_b: uuid.UUID = Query(..., alias="raceB"),  # noqa: B008
) -> SuccessResponse[RaceComparison]:
    data = await compare_service.compare_races(db, race_a, race_b)
    return SuccessResponse(data=data, meta=build_meta(request))
