"""Registers centralized exception handlers on the FastAPI app.

Every error response follows the standard envelope from
docs/05_BACKEND_ARCHITECTURE.md / docs/08_API_SPECIFICATION.md:

    {"success": false, "error": {"code": "...", "message": "..."}, "request_id": "..."}
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.base import AppException
from app.schemas.common import ErrorDetail, ErrorResponse

logger = logging.getLogger("app.exceptions")


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _envelope(
    code: str, message: str, request: Request, *, details: list[dict[str, Any]] | None = None
) -> dict[str, object]:
    error = ErrorDetail(code=code, message=message, details=details)
    return ErrorResponse(error=error, request_id=_request_id(request)).model_dump()


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope(exc.code, exc.message, request),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope("HTTP_ERROR", str(exc.detail), request),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    content = _envelope(
        "VALIDATION_ERROR",
        "Request validation failed.",
        request,
        details=jsonable_encoder(exc.errors()),
    )
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=content)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception", extra={"request_id": _request_id(request)})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_envelope("INTERNAL_ERROR", "An unexpected error occurred.", request),
    )


def register_exception_handlers(app: FastAPI) -> None:
    # Starlette's typeshed signature for add_exception_handler is wider than
    # any single handler needs to be; the runtime dispatches correctly based
    # on the registered exception class.
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
