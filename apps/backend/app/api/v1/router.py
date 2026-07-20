"""Aggregates every v1 resource router.

Future routers (races, circuits, comparison, search, ...) will each be
included here as they're built, per docs/08_API_SPECIFICATION.md.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.constructors import router as constructors_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.drivers import router as drivers_router
from app.api.v1.seasons import router as seasons_router

api_router = APIRouter()
api_router.include_router(dashboard_router)
api_router.include_router(seasons_router)
api_router.include_router(drivers_router)
api_router.include_router(constructors_router)
