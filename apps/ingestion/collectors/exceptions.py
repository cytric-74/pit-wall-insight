"""Collector-level failures.

Purpose
-------
Distinguishes two fundamentally different failure modes so callers (and
future loader/pipeline code) can react to them differently:

1. A *source* is unreachable or erroring (network down, upstream 5xx, rate
   limited) — nothing was collected at all. This is `SourceUnavailableError`.
2. A source responded successfully, but its response didn't have the shape
   this collector knows how to flatten (e.g. Jolpica's `MRData` envelope is
   missing an expected nested key because the API changed). This is
   `UnexpectedResponseShapeError`.

Neither of these is the same thing as "one record in an otherwise-good batch
failed validation" — that's `validators.validate.ValidationIssue`, which is
data, not an exception, precisely because a single bad record must not abort
processing of the rest of the batch (docs/06_DATA_ENGINEERING.md:
"Validation failures are logged. Pipeline should continue where possible.").
These two exceptions, by contrast, mean the collector has nothing usable to
hand back at all, so raising is correct.
"""

from __future__ import annotations


class CollectorError(Exception):
    """Base class for every exception raised by `collectors/`."""


class SourceUnavailableError(CollectorError):
    """The upstream source could not be reached or returned an error status.

    Raised for network failures, timeouts, and non-2xx HTTP responses that
    indicate the *source itself* is the problem, not the data it holds.
    """


class UnexpectedResponseShapeError(CollectorError):
    """The upstream source responded, but not in the shape this collector expects.

    Raised when a required top-level key is missing from a response (e.g. a
    FastF1 session that failed to load a data category, or a Jolpica
    response missing its `MRData` envelope). This signals an API contract
    change or a genuinely unsupported query (e.g. a session type that didn't
    exist in a given season) rather than a single bad data point.
    """
