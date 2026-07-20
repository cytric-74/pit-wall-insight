"""Jolpica-F1 collector — the secondary/historical data source (docs/06_DATA_ENGINEERING.md).

Purpose
-------
Provides season calendars, driver/constructor championship standings, and
race results going back to 1950 — coverage FastF1 does not have, since
FastF1's own session-level data only reliably exists from the 2018 season
onward (see `F1ApiSupport` in `fastf1_client.get_event_schedule`). This
project calls this data "Ergast" throughout the documentation
(`docs/06_DATA_ENGINEERING.md` names it as the secondary source), but the
literal `ergast.com` API was retired in 2024 and now redirects rather than
serving JSON. **Jolpica-F1** (`https://api.jolpi.ca/ergast/f1`) is the
community-maintained, byte-for-byte-compatible successor: identical
endpoint paths, identical `MRData` JSON envelope, no API key. Every
function in this module hits Jolpica; "Ergast" in this codebase means
"whatever serves the Ergast API contract," which today is Jolpica.

Inputs
------
A season (`year`), and for race-level results, a round number.

Outputs
-------
Raw, unvalidated records as plain dicts, with Ergast's own field names
(e.g. `"driverId"`, `"constructorId"`, `"points"`) — already unwrapped from
Ergast's deeply-nested `MRData` envelope (see `_extract_list`), but
otherwise unmodified, per the same collector contract `fastf1_client.py`
follows (see `collectors/__init__.py`).

Edge cases
----------
- Ergast/Jolpica paginates any list that can exceed its default page size
  (30 items) using `limit`/`offset` query parameters and a `total` count in
  every response. `_get_paginated` follows this until every page has been
  fetched, rather than silently returning only the first 30 results for
  something like a full season's race list.
- A season with no data yet (e.g. a future season before any standings
  exist) returns an empty list, not an error — Jolpica responds with `200`
  and an empty inner list in that case, which this module treats as valid,
  empty data rather than a failure.
- Network failures and non-2xx responses raise `SourceUnavailableError`;
  a `200` response missing its expected `MRData` structure raises
  `UnexpectedResponseShapeError` (see `collectors/exceptions.py` for why
  these are kept distinct from per-record validation failures).
"""

from __future__ import annotations

from typing import Any

import requests

from collectors.exceptions import SourceUnavailableError, UnexpectedResponseShapeError
from config.settings import get_settings

# Jolpica's own default and hard maximum page size, per its API
# documentation (mirroring the original Ergast API's limits). Requesting
# more than this in a single page is rejected by the server, so pagination
# always steps by this amount rather than trying to guess a larger one.
_PAGE_SIZE = 100

# In-process response cache, keyed by (path, sorted params) — unlike
# `fastf1_client.py`'s on-disk cache (safe because a finished FastF1
# session never changes), Jolpica's calendar/standings/results calls were
# re-fetched from the network on every single call within a run, even for
# a season that's long concluded and can never change again (Phase 7
# audit, Medium). Scoped to one process's lifetime only, not persisted to
# disk — a `collect` invocation that legitimately needs the current
# season's still-changing standings gets a fresh process (and therefore a
# fresh cache) every run, so this never serves stale in-progress-season
# data across runs.
_response_cache: dict[tuple[str, tuple[tuple[str, Any], ...]], dict[str, Any]] = {}


def _get(path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Issue a single GET request against the configured Jolpica base URL.

    Inputs: `path` — the endpoint path *after* the base URL, e.g.
    `"2024.json"` or `"2024/driverStandings.json"`. `params` — query
    parameters (`limit`, `offset`).

    Outputs: the parsed JSON response body as a dict — still in Ergast's
    native `MRData`-wrapped shape; unwrapping happens in `_extract_list`,
    kept as a separate step so callers that need the envelope's metadata
    (e.g. `total`, for pagination) can still get at it. Repeating an
    identical `(path, params)` call within the same process returns the
    cached body rather than hitting the network again (see
    `_response_cache` above).

    Edge cases: raises `SourceUnavailableError` for connection failures,
    timeouts, and non-2xx status codes — anything indicating the request
    itself failed, as opposed to succeeding with a body this module doesn't
    recognize (that's `UnexpectedResponseShapeError`, raised by
    `_extract_list` instead, since only the caller who knows the expected
    shape can detect that). Only a successful response is cached — a
    failed call is retried on its next call, not remembered as a failure.
    """
    cache_key = (path, tuple(sorted((params or {}).items())))
    cached = _response_cache.get(cache_key)
    if cached is not None:
        return cached

    settings = get_settings()
    url = f"{settings.jolpica_base_url.rstrip('/')}/{path.lstrip('/')}"
    headers = {"User-Agent": settings.user_agent}

    try:
        response = requests.get(
            url, params=params, headers=headers, timeout=settings.request_timeout_seconds
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SourceUnavailableError(f"Jolpica-F1 request failed: GET {url} ({exc})") from exc

    result: dict[str, Any] = response.json()
    _response_cache[cache_key] = result
    return result


def _extract_list(payload: dict[str, Any], *keys: str) -> tuple[list[dict[str, Any]], int]:
    """Walk a nested key path inside an `MRData` envelope and return the list found there, plus the reported total.

    Inputs: `payload` — the raw dict from `_get`. `keys` — the nested key
    path to the list this endpoint actually cares about, e.g.
    `("RaceTable", "Races")` for a calendar response, or
    `("StandingsTable", "StandingsLists")` for a standings response
    (the caller then indexes into the first element of that list itself,
    since standings responses nest one more level than calendar/results
    responses do — see `get_driver_standings`).

    Outputs: `(items, total)` — `items` is the list found at the end of the
    key path (or `[]` if any intermediate key is present but its value is
    an empty list — a valid "no data yet" response, not an error). `total`
    is Ergast's own `MRData.total` field, used by `_get_paginated` to know
    when every page has been fetched.

    Edge case: raises `UnexpectedResponseShapeError` only when the
    `MRData` envelope itself, or one of the requested intermediate keys, is
    *missing entirely* — that indicates the API contract changed or the
    response isn't from this API at all, not that the data is simply empty.
    """
    try:
        mr_data = payload["MRData"]
        total = int(mr_data["total"])
        node: Any = mr_data
        for key in keys:
            node = node[key]
    except (KeyError, TypeError, ValueError) as exc:
        raise UnexpectedResponseShapeError(
            f"Jolpica-F1 response missing expected key path {keys!r}: {exc}"
        ) from exc

    if not isinstance(node, list):
        raise UnexpectedResponseShapeError(
            f"Jolpica-F1 response at key path {keys!r} was not a list: {type(node)!r}"
        )
    return node, total


def _get_paginated(path: str, *keys: str) -> list[dict[str, Any]]:
    """Fetch every page of a Jolpica endpoint and return the combined list.

    Why this exists: Ergast/Jolpica caps every response at a page size
    (`limit`, defaulting to 30 if unspecified; this module always passes
    `_PAGE_SIZE` explicitly) and reports how many *total* items exist across
    all pages. A season's full race results, for example, can exceed one
    page; reading only `_get`'s first response would silently drop data.

    Time complexity: O(⌈total / _PAGE_SIZE⌉) HTTP requests — the minimum
    possible given the API's pagination contract, since there's no bulk/
    unpaged endpoint to fall back to.

    Edge case: a response reporting `total=0` (no data for this query yet)
    returns `[]` after exactly one request; this function never guesses at
    a page count in advance, it always trusts the server-reported total
    from the *first* page's response.
    """
    offset = 0
    combined: list[dict[str, Any]] = []
    while True:
        payload = _get(path, params={"limit": _PAGE_SIZE, "offset": offset})
        items, total = _extract_list(payload, *keys)
        combined.extend(items)
        offset += len(items)
        if offset >= total or not items:
            break
    return combined


def get_season_calendar(year: int) -> list[dict[str, Any]]:
    """Return every round on a season's calendar, going back to 1950.

    Outputs: one record per round, with Ergast's own field names
    (`round`, `raceName`, `date`, `time`, and a nested `Circuit` object
    with `circuitId`/`circuitName`/`Location`). Maps to `dim_season` and
    the calendar-shaping half of `dim_circuit` (docs/07_DATABASE_SCHEMA.md)
    for seasons FastF1's schedule doesn't cover in detail.
    """
    return _get_paginated(f"{year}.json", "RaceTable", "Races")


def get_driver_standings(year: int) -> list[dict[str, Any]]:
    """Return final (or current, for an in-progress season) driver championship standings.

    Outputs: one record per classified driver, with Ergast's own field
    names (`position`, `points`, `wins`, and a nested `Driver` object).
    Maps to the driver half of `mart_dashboard` / season standings
    (docs/07_DATABASE_SCHEMA.md, docs/08_API_SPECIFICATION.md
    `/seasons/{season}/standings`).

    Edge case: Ergast/Jolpica nests standings one level deeper than
    calendar/results responses — `StandingsTable.StandingsLists` is itself
    a list (historically, to support multi-round-range queries), so this
    function indexes into element `[0]` after `_extract_list` resolves the
    outer list. A season with no standings computed yet yields an empty
    `StandingsLists`, in which case this returns `[]` rather than raising.
    """
    lists, _ = _extract_list(
        _get(f"{year}/driverStandings.json", params={"limit": _PAGE_SIZE}),
        "StandingsTable",
        "StandingsLists",
    )
    if not lists:
        return []
    result: list[dict[str, Any]] = lists[0].get("DriverStandings", [])
    return result


def get_constructor_standings(year: int) -> list[dict[str, Any]]:
    """Return final (or current, for an in-progress season) constructor championship standings.

    Outputs: one record per classified constructor, with Ergast's own field
    names (`position`, `points`, `wins`, and a nested `Constructor` object).
    Same nesting/edge-case behavior as `get_driver_standings`, see there for
    detail.
    """
    lists, _ = _extract_list(
        _get(f"{year}/constructorStandings.json", params={"limit": _PAGE_SIZE}),
        "StandingsTable",
        "StandingsLists",
    )
    if not lists:
        return []
    result: list[dict[str, Any]] = lists[0].get("ConstructorStandings", [])
    return result


def get_race_results(year: int, round_number: int) -> list[dict[str, Any]]:
    """Return classified results for one specific race.

    Inputs: `year` and `round_number` (1-indexed, matching the calendar
    `round` field from `get_season_calendar`).

    Outputs: one record per driver, with Ergast's own field names
    (`position`, `points`, `status`, `grid`, `Time`, nested `Driver` and
    `Constructor` objects). This is the fallback source for `fct_results`
    (docs/07_DATABASE_SCHEMA.md) for seasons FastF1 doesn't have session
    data for; for FastF1-supported seasons,
    `fastf1_client.get_session_results` is preferred as the richer source
    (see the source-of-truth table in the implementation plan).

    Edge case: a round number that doesn't exist for the given season
    (e.g. round 30 in a 24-race season) yields an empty
    `RaceTable.Races` list, which this function returns as `[]` rather
    than raising — the caller asked a question with no answer, not one
    that violated the API's contract.
    """
    races, _ = _extract_list(
        _get(f"{year}/{round_number}/results.json", params={"limit": _PAGE_SIZE}),
        "RaceTable",
        "Races",
    )
    if not races:
        return []
    result: list[dict[str, Any]] = races[0].get("Results", [])
    return result
