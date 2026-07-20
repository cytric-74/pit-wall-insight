"""Aggregates every v1 resource router, per docs/08_API_SPECIFICATION.md."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.circuits import router as circuits_router
from app.api.v1.compare import router as compare_router
from app.api.v1.constructors import router as constructors_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.drivers import router as drivers_router
from app.api.v1.races import router as races_router
from app.api.v1.search import router as search_router
from app.api.v1.seasons import router as seasons_router
from app.api.v1.sessions import router as sessions_router
from app.api.v1.strategy import router as strategy_router

api_router = APIRouter()
api_router.include_router(dashboard_router)
api_router.include_router(seasons_router)
api_router.include_router(drivers_router)
api_router.include_router(constructors_router)
api_router.include_router(races_router)
api_router.include_router(sessions_router)
api_router.include_router(circuits_router)
api_router.include_router(compare_router)
api_router.include_router(search_router)
api_router.include_router(strategy_router)
