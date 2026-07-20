"""FastAPI application entry point.

Run locally with:

    uvicorn app.main:app --reload --app-dir apps/backend
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    # No rate limiting exists in-process — every route (notably `/search`
    # and `/strategy/tyres`, both unauthenticated and expensive) is
    # unprotected against scraping or abuse at the application layer
    # (Phase 7 audit, High). This must be enforced at the reverse-proxy/API
    # gateway layer before any public deployment; see docs/11_DEPLOYMENT.md
    # ("Security" -> "Rate Limiting") for the explicit requirement.
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(api_v1_router, prefix=settings.api_prefix)

    return app


app = create_app()
