"""Base application exception.

Feature-specific exceptions (raised from `app/services/`) will subclass
`AppException` once business logic exists. None do yet.
"""

from __future__ import annotations


class AppException(Exception):
    """Base class for every application-raised (as opposed to framework-raised) error."""

    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, *, code: str | None = None, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code


class NotFoundError(AppException):
    status_code = 404
    code = "NOT_FOUND"


class ValidationError(AppException):
    status_code = 422
    code = "VALIDATION_ERROR"
