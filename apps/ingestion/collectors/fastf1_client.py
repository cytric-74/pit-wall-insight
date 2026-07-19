"""FastF1 collector — the primary Formula One data source (docs/06_DATA_ENGINEERING.md).

Purpose
-------
Wraps the third-party `fastf1` library so the rest of the ingestion
pipeline never imports `fastf1` directly. That indirection buys two things:

1. **Cache correctness.** `fastf1.Cache.enable_cache(...)` must run before
   any other `fastf1` call in the process, exactly once. Funnelling every
   FastF1 access through this module means that invariant only has to be
   enforced in one place (`ensure_cache_enabled`) instead of remembered at
   every call site.
2. **A stable, pandas-free return type.** FastF1 returns pandas DataFrames
   (`EventSchedule`, `session.results`, `session.laps`,
   `session.weather_data`). Everything downstream of this module —
   validators, and eventually loaders — should not need to know pandas
   exists. Every public function here returns `list[dict[str, Any]]`, with
   `NaN`/`NaT` normalized to `None` and `Timestamp`/`Timedelta` values
   normalized to plain, JSON-serializable types. This is *not* a validation
   or business-logic step (see `collectors/__init__.py`) — it's the same
   data, just represented without a pandas dependency leaking outward.

Inputs
------
A season (`year`), and for session-level functions, an event identifier
(`event` — accepts anything `fastf1.get_session` accepts: a round number,
or a country/location/event name substring) and a session type
(`"FP1"`, `"FP2"`, `"FP3"`, `"Q"`, `"S"`, `"SQ"`, `"R"`).

Outputs
-------
Raw, unvalidated records as plain dicts, keyed by FastF1's own column names
(e.g. `"LapTime"`, `"TrackTemp"`) — deliberately *not* renamed to this
project's `raw_*` column names yet, since renaming is schema work that
belongs to `validators/schema.py`, not to a collector.

Edge cases
----------
- A session that doesn't exist for a given year/event (e.g. requesting a
  Sprint session for a weekend that didn't have one) raises whatever
  `fastf1` itself raises; this module does not swallow that, because it
  means the caller asked for something that was never going to exist, which
  is a caller error rather than a transient data problem.
- Loading is scoped per function (`_load_session` only requests the data
  categories that function actually needs) because a full `session.load()`
  with telemetry enabled can take tens of seconds to minutes per session —
  requesting only `laps` or only `weather` keeps this phase's calls fast,
  and telemetry itself is out of scope for this phase entirely (see
  docs/07_DATABASE_SCHEMA.md `fct_telemetry`, deferred to a future phase).
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, cast

import fastf1
import pandas as pd

from config.settings import get_settings

# Guards `fastf1.Cache.enable_cache` so it only ever runs once per process,
# regardless of how many times `ensure_cache_enabled` is called. FastF1's
# own cache module is a global (module-level) singleton, so re-enabling it
# with the same path is harmless but wasteful; this flag makes the
# "exactly once" invariant explicit and independently testable rather than
# relying on import-time side effects that are awkward to assert on in
# tests.
_cache_enabled = False


def ensure_cache_enabled() -> None:
    """Enable FastF1's on-disk response cache, exactly once per process.

    Why this exists: every FastF1 call this module makes goes over the
    network to F1's live timing archive unless a local cache satisfies it
    first. Historical session data never changes once a session has
    finished, so re-fetching it on every pipeline run would be pure waste —
    slower runs, and unnecessary load on FastF1's upstream. The cache
    directory comes from `Settings.fastf1_cache` (env var `FASTF1_CACHE`,
    default `./.fastf1_cache`) rather than a hardcoded path, so deployments
    can point it at a persistent volume.

    Edge case: FastF1 requires the cache directory to already exist on
    disk — it does not create parent directories itself. This function
    creates it first (`parents=True, exist_ok=True`), so a fresh checkout
    with no `.fastf1_cache` directory works without any manual setup step.
    """
    global _cache_enabled
    if _cache_enabled:
        return

    cache_dir = Path(get_settings().fastf1_cache)
    cache_dir.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))
    _cache_enabled = True


def _normalize_value(value: Any) -> Any:
    """Convert a single pandas cell value into a plain, JSON-serializable value.

    FastF1's DataFrames mix native Python types with pandas-specific ones:

    - `NaN` (missing numeric data) and `NaT` (missing timestamp/timedelta
      data) both fail `json.dumps` and are semantically "no value" — both
      normalize to `None`.
    - `pandas.Timestamp` (e.g. `EventDate`, `LapStartDate`) normalizes to an
      ISO 8601 string, so a downstream Pydantic model can parse it as a
      `datetime` without importing pandas.
    - `pandas.Timedelta` (e.g. `LapTime`, `Sector1Time`, `Q1`) normalizes to
      total seconds as a `float`, which is the natural representation for a
      duration and matches `docs/07_DATABASE_SCHEMA.md`'s `INTERVAL` /
      numeric timing convention without requiring an ISO-8601 duration
      parser downstream.
    - Anything else (str, int, float, bool) passes through unchanged.

    Time complexity: O(1) per call; this function does no iteration.
    """
    if isinstance(value, float) and math.isnan(value):
        return None
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, pd.Timedelta):
        return value.total_seconds()
    return value


def _dataframe_to_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Flatten a FastF1 DataFrame into a list of plain dicts.

    Inputs: any DataFrame FastF1 returns (event schedule, results, laps,
    weather) — all of them are one-row-per-record already, so no
    reshaping is needed, only per-cell normalization.

    Outputs: `list[dict[str, Any]]`, one dict per DataFrame row, column
    names preserved exactly as FastF1 names them.

    Implementation note: rows are converted to plain dicts via
    `to_dict(orient="records")` *before* any value normalization runs, and
    `_normalize_value` is then applied to each dict's values directly —
    deliberately not via `DataFrame.map`, which reconstructs a DataFrame
    from the mapped values. That reconstruction silently undoes the very
    normalization this function exists to do: assigning Python `None` into
    a pandas column pandas infers as numeric coerces it straight back to
    `NaN`, so a `NaT` in a `Timedelta` column would `map` to `None` and
    then immediately become `NaN` again on reassembly. Normalizing plain
    Python dicts, with no DataFrame reconstruction step in between, avoids
    that coercion entirely.

    Time complexity: O(rows x columns) — every cell is visited exactly
    once; there is no way to flatten a DataFrame in less than that, since
    every cell may independently need normalizing (a `NaN` next to a valid
    value in the same column is common in FastF1 data, e.g. a lap with no
    recorded `Sector3Time` because the driver retired mid-lap).
    """
    # `DataFrame.to_dict(orient="records")` is typed by pandas-stubs as
    # `list[dict[Hashable, Any]]` (a DataFrame's columns are `Hashable` in
    # general), but every FastF1 DataFrame this module handles has plain
    # string column names — the cast reflects that narrower, true-in-
    # practice guarantee rather than widening this function's own contract.
    raw_records = cast(list[dict[str, Any]], frame.to_dict(orient="records"))
    return [
        {column: _normalize_value(value) for column, value in record.items()}
        for record in raw_records
    ]


def get_event_schedule(year: int, *, include_testing: bool = False) -> list[dict[str, Any]]:
    """Return every event (race weekend) on a season's calendar.

    Inputs: `year` — a season, e.g. `2024`. `include_testing` — whether to
    include pre-season testing "events" FastF1 also tracks; defaults to
    `False` because testing sessions have no results/standings and aren't
    part of `dim_season`'s `race_count` (docs/07_DATABASE_SCHEMA.md).

    Outputs: one record per event, with FastF1's own column names
    (`RoundNumber`, `EventName`, `Country`, `Location`, `EventDate`,
    `Session1`..`Session5`, `Session1Date`..`Session5Date`,
    `F1ApiSupport`). `F1ApiSupport` is worth calling out: it's `False` for
    older seasons FastF1 has schedule data for but no session-level
    telemetry/results for — a downstream consumer deciding whether to
    attempt `get_session_results` for a given event should check this flag
    first rather than discovering the gap via a failed call.

    Edge case: `year` values before FastF1's supported range (roughly 1950
    for calendar-only data, 2018+ for full session support) still return a
    schedule for seasons Ergast/FastF1's schedule backend knows about, but
    with all `F1ApiSupport` values `False` — an empty list is only
    returned for a `year` that has no F1 season at all (e.g. a future year
    with no announced calendar yet).
    """
    ensure_cache_enabled()
    schedule = fastf1.get_event_schedule(year, include_testing=include_testing)
    return _dataframe_to_records(schedule)


def _load_session(
    year: int, event: str | int, session_type: str, *, laps: bool, weather: bool
) -> fastf1.core.Session:
    """Fetch and load a single session, requesting only the data categories needed.

    Inputs: `year`/`event`/`session_type` identify the session exactly as
    `fastf1.get_session` expects them. `laps`/`weather` control which data
    categories `Session.load` fetches; `telemetry` and `messages` are always
    `False` here — telemetry is out of scope for this phase entirely (100ms
    samples belong to a future `fct_telemetry` phase), and race control
    messages aren't consumed by any collector function yet.

    Outputs: a loaded `fastf1.core.Session`, ready for `.results`, `.laps`,
    or `.weather_data` to be read off it depending on what the caller
    requested.

    Edge case: requesting `laps=True` for a session type that has no laps
    (e.g. that almost never happens for real F1 sessions, but a
    cancelled/red-flagged session can have zero recorded laps) yields a
    successfully-loaded session with an empty `laps` DataFrame — not an
    error. Callers see this as an empty list, not an exception, which is
    the correct signal: the session existed, it simply produced no lap
    data.
    """
    ensure_cache_enabled()
    session = fastf1.get_session(year, event, session_type)
    session.load(laps=laps, telemetry=False, weather=weather, messages=False)
    return session


def get_session_results(year: int, event: str | int, session_type: str) -> list[dict[str, Any]]:
    """Return classification results for one session.

    Outputs: one record per driver, with FastF1's own column names
    (`DriverId`, `Abbreviation`, `TeamName`, `Position`, `GridPosition`,
    `Q1`/`Q2`/`Q3` as second-durations after normalization, `Status`,
    `Points`). This is the primary source for `fct_results`
    (docs/07_DATABASE_SCHEMA.md) for seasons FastF1 supports.
    """
    session = _load_session(year, event, session_type, laps=False, weather=False)
    return _dataframe_to_records(session.results)


def get_session_laps(year: int, event: str | int, session_type: str) -> list[dict[str, Any]]:
    """Return every recorded lap for one session, across all drivers.

    Outputs: one record per driver-lap, with FastF1's own column names
    (`Driver`, `LapNumber`, `LapTime`, `Sector1Time`/`Sector2Time`/
    `Sector3Time`, `Compound`, `TyreLife`, `PitInTime`/`PitOutTime`,
    `Position`). This is the primary — and only — source for `fct_laps`
    and `fct_pitstop` (docs/07_DATABASE_SCHEMA.md): lap-by-lap and pit-stop
    granularity does not exist in Ergast/Jolpica at all, historical or
    otherwise.

    `PitInTime`/`PitOutTime` are worth calling out for a future loader: a
    lap where both are populated is a pit stop; `fct_pitstop` is derived
    from this same lap data rather than fetched from a separate endpoint.
    """
    session = _load_session(year, event, session_type, laps=True, weather=False)
    return _dataframe_to_records(session.laps)


def get_session_weather(year: int, event: str | int, session_type: str) -> list[dict[str, Any]]:
    """Return weather samples recorded throughout one session.

    Outputs: one record per weather sample (FastF1 samples roughly once a
    minute), with FastF1's own column names (`Time` — a `Timedelta` offset
    from session start, not a wall-clock timestamp, normalized to seconds
    like any other duration — `AirTemp`, `TrackTemp`, `Humidity`,
    `Pressure`, `Rainfall`, `WindDirection`, `WindSpeed`). Maps directly to
    `dim_weather` (docs/07_DATABASE_SCHEMA.md).
    """
    session = _load_session(year, event, session_type, laps=False, weather=True)
    return _dataframe_to_records(session.weather_data)
