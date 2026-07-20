"""Request ID + timing middleware.

Every request logs timestamp, endpoint, method, duration, and status code
(see docs/05_BACKEND_ARCHITECTURE.md — "Logging"), and every response carries
an `X-Request-ID` header so it can be correlated with the standard error
envelope's `request_id` field.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.request")

REQUEST_ID_HEADER = "X-Request-ID"


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attaches a request ID to `request.state` and logs request timing."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER, str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.perf_counter()
        # Also stashed on `request.state` (not just used locally here) so
        # `app.utils.responses.build_meta` can compute the same elapsed time
        # for the response body's `meta.execution_time` field — the one
        # place other than this middleware that needs to know when the
        # request started.
        request.state.start_time = start_time
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        response.headers[REQUEST_ID_HEADER] = request_id
        logger.info(
            "request handled",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )
        return response
