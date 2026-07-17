"""Logging configuration.

Development gets human-readable console output. Staging/production get
structured JSON so log aggregators (and eventually Grafana/Loki, per
docs/11_DEPLOYMENT.md) can parse fields directly.
"""

from __future__ import annotations

import logging.config

from app.core.config import Environment, Settings

_CONSOLE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def build_logging_config(settings: Settings) -> dict[str, object]:
    json_formatter: dict[str, object] = {
        "()": "pythonjsonlogger.json.JsonFormatter",
        "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
    }
    console_formatter: dict[str, object] = {"format": _CONSOLE_FORMAT}

    use_json = settings.environment in (Environment.STAGING, Environment.PRODUCTION)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": console_formatter,
            "json": json_formatter,
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "json" if use_json else "console",
            },
        },
        "root": {
            "handlers": ["default"],
            "level": settings.log_level.upper(),
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": settings.log_level.upper(), "propagate": False},
            "uvicorn.access": {"handlers": ["default"], "level": settings.log_level.upper(), "propagate": False},
        },
    }


def configure_logging(settings: Settings) -> None:
    logging.config.dictConfig(build_logging_config(settings))
