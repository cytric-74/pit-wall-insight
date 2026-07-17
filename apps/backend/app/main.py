"""FastAPI application entry point.

Run locally with:

    uvicorn app.main:app --reload --app-dir apps/backend
"""

from __future__ import annotations

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.v1.router import api_router as api_v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.exceptions.handlers import register_exception_handlers
from app.middleware.request_context import RequestContextMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.project_name,
        version=settings.api_version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(api_v1_router, prefix=settings.api_prefix)

    return app


app = create_app()
