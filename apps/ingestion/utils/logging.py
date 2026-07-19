"""Pipeline-stage logging (`docs/06_DATA_ENGINEERING.md` "Pipeline Monitoring").

Purpose
-------
The docs ask every pipeline run to log a specific sequence of stages
("Pipeline Start -> API Calls -> Validation -> Insert Count -> Transform
Time -> dbt Tests -> Pipeline End") and require that "failures identify the
exact stage." `PipelineLogger` is a small, generic stage-timer that
satisfies this without knowing anything about what a "stage" actually
does — it only needs a name. That's a deliberate scope boundary: this
phase only ever logs "collect" and "validate" stages; future phases will
add "load" and "transform" stages by calling the exact same `stage()`
method with a different name, with no change needed here.

Inputs
------
A stage name (e.g. `"collect:fastf1.get_event_schedule"`), passed to the
`stage()` context manager.

Outputs
-------
Structured log lines via the standard library `logging` module (so they
flow through whatever handler/formatter the process configures — this
module never configures logging itself, only emits to a named logger),
recording each stage's start, duration, and outcome.

Edge cases
----------
An exception raised inside a `with pipeline_logger.stage(...)` block is
logged — with the stage name and elapsed time up to the failure point —
and then re-raised unchanged. This module never swallows an error; it only
ever adds context to one, per the docs' "failures should identify the
exact stage."
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager

logger = logging.getLogger("ingestion.pipeline")


class PipelineLogger:
    """Logs the start, duration, and outcome of named pipeline stages.

    One instance is meant to represent one pipeline *run* (as opposed to
    one stage) — `run_id` is attached to every log line this instance
    produces, so that if multiple runs' log output ends up interleaved
    (concurrent processes, or sequential runs whose logs weren't rotated
    between them) each line can still be attributed to the run that
    produced it.
    """

    def __init__(self, run_id: str) -> None:
        self._run_id = run_id

    def event(self, message: str, **fields: object) -> None:
        """Log a single, non-timed pipeline fact (e.g. a record count).

        Inputs: `message` — a short human-readable description.
        `fields` — arbitrary key/value pairs appended to the log line
        (e.g. `valid_count=57, issue_count=2`), for facts that don't have a
        natural start/end shape the way a `stage()` does.
        """
        extra = " ".join(f"{key}={value}" for key, value in fields.items())
        logger.info("[run=%s] %s %s", self._run_id, message, extra)

    @contextmanager
    def stage(self, name: str) -> Iterator[None]:
        """Time and log one named pipeline stage.

        Usage::

            with pipeline_logger.stage("collect:fastf1.get_event_schedule"):
                records = get_event_schedule(2024)

        On success, logs the stage name and elapsed wall-clock time in
        milliseconds. On failure, logs the same information (with the
        exception, via `logger.exception`) and then re-raises — this
        satisfies "failures should identify the exact stage" without ever
        hiding the failure from the caller, since a swallowed exception
        here would mean a broken pipeline run silently looks like a
        successful one.
        """
        started = time.monotonic()
        logger.info("[run=%s] stage started: %s", self._run_id, name)
        try:
            yield
        except Exception:
            elapsed_ms = (time.monotonic() - started) * 1000
            logger.exception("[run=%s] stage failed: %s (after %.1fms)", self._run_id, name, elapsed_ms)
            raise
        else:
            elapsed_ms = (time.monotonic() - started) * 1000
            logger.info("[run=%s] stage completed: %s (%.1fms)", self._run_id, name, elapsed_ms)
