"""Unit tests for `collectors.fastf1_client`.

No network access happens in this file — every `fastf1` call is mocked, so
these tests verify this module's own logic (cache-enable idempotency,
value normalization, DataFrame flattening, and that each public function
requests the right data categories from `Session.load`) rather than
FastF1's behavior itself. Real connectivity is covered separately by
`test_collectors_network.py`, marked `@pytest.mark.network` and excluded
from this default run.
"""

from __future__ import annotations

import math
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests
from fastf1.exceptions import InvalidSessionError, NoLapDataError, RateLimitExceededError

import collectors.fastf1_client as fastf1_client
from collectors.exceptions import SourceUnavailableError, UnexpectedResponseShapeError
from collectors.fastf1_client import (
    _dataframe_to_records,
    _normalize_value,
    ensure_cache_enabled,
    get_event_schedule,
    get_session_laps,
    get_session_results,
    get_session_weather,
)


@pytest.fixture(autouse=True)
def _reset_cache_flag() -> None:
    """Reset the module-level "cache already enabled" guard before every
    test in this file, so tests don't leak state into one another via
    import-level singleton behavior."""
    fastf1_client._cache_enabled = False


def test_ensure_cache_enabled_creates_the_cache_directory(tmp_path) -> None:  # type: ignore[no-untyped-def]
    cache_dir = tmp_path / "does" / "not" / "exist" / "yet"
    with (
        patch("collectors.fastf1_client.get_settings") as mock_get_settings,
        patch("collectors.fastf1_client.fastf1.Cache.enable_cache") as mock_enable_cache,
    ):
        mock_get_settings.return_value = MagicMock(fastf1_cache=str(cache_dir))
        ensure_cache_enabled()

    assert cache_dir.is_dir()
    mock_enable_cache.assert_called_once_with(str(cache_dir))


def test_ensure_cache_enabled_only_enables_the_cache_once(tmp_path) -> None:  # type: ignore[no-untyped-def]
    with (
        patch("collectors.fastf1_client.get_settings") as mock_get_settings,
        patch("collectors.fastf1_client.fastf1.Cache.enable_cache") as mock_enable_cache,
    ):
        mock_get_settings.return_value = MagicMock(fastf1_cache=str(tmp_path))
        ensure_cache_enabled()
        ensure_cache_enabled()
        ensure_cache_enabled()

    mock_enable_cache.assert_called_once()


class TestNormalizeValue:
    def test_nan_becomes_none(self) -> None:
        assert _normalize_value(float("nan")) is None

    def test_pandas_na_becomes_none(self) -> None:
        assert _normalize_value(pd.NA) is None

    def test_nat_becomes_none(self) -> None:
        assert _normalize_value(pd.NaT) is None

    def test_timestamp_becomes_iso_string(self) -> None:
        timestamp = pd.Timestamp("2024-03-02T15:00:00Z")
        result = _normalize_value(timestamp)
        assert result == timestamp.isoformat()

    def test_timedelta_becomes_total_seconds(self) -> None:
        delta = pd.Timedelta(seconds=92, milliseconds=741)
        result = _normalize_value(delta)
        assert math.isclose(result, 92.741)

    def test_ordinary_values_pass_through_unchanged(self) -> None:
        assert _normalize_value("VER") == "VER"
        assert _normalize_value(44) == 44
        assert _normalize_value(True) is True


def test_dataframe_to_records_flattens_rows_and_normalizes_missing_values() -> None:
    frame = pd.DataFrame(
        {
            "Driver": ["VER", "NOR"],
            "LapTime": [pd.Timedelta(seconds=91.2), pd.NaT],
        }
    )

    records = _dataframe_to_records(frame)

    assert records == [
        {"Driver": "VER", "LapTime": 91.2},
        {"Driver": "NOR", "LapTime": None},
    ]


def _mock_session(**data_frames: pd.DataFrame) -> MagicMock:
    """Build a mock `fastf1.core.Session` exposing only the attributes
    `fastf1_client` reads (`.load()` and whichever of `.results`/`.laps`/
    `.weather_data` the test cares about)."""
    session = MagicMock()
    for name, frame in data_frames.items():
        setattr(session, name, frame)
    return session


def test_get_event_schedule_flattens_the_schedule_dataframe() -> None:
    schedule = pd.DataFrame({"RoundNumber": [1], "EventName": ["Bahrain Grand Prix"]})
    with (
        patch("collectors.fastf1_client.ensure_cache_enabled"),
        patch("collectors.fastf1_client.fastf1.get_event_schedule", return_value=schedule) as mock_get,
    ):
        records = get_event_schedule(2024)

    mock_get.assert_called_once_with(2024, include_testing=False)
    assert records == [{"RoundNumber": 1, "EventName": "Bahrain Grand Prix"}]


def test_get_session_results_loads_only_results_and_flattens_them() -> None:
    results = pd.DataFrame({"Abbreviation": ["VER"], "Points": [25.0]})
    session = _mock_session(results=results)
    with (
        patch("collectors.fastf1_client.ensure_cache_enabled"),
        patch("collectors.fastf1_client.fastf1.get_session", return_value=session) as mock_get,
    ):
        records = get_session_results(2024, 1, "R")

    mock_get.assert_called_once_with(2024, 1, "R")
    session.load.assert_called_once_with(laps=False, telemetry=False, weather=False, messages=False)
    assert records == [{"Abbreviation": "VER", "Points": 25.0}]


def test_get_session_laps_requests_only_laps() -> None:
    laps = pd.DataFrame({"Driver": ["VER"], "LapNumber": [1.0]})
    session = _mock_session(laps=laps)
    with (
        patch("collectors.fastf1_client.ensure_cache_enabled"),
        patch("collectors.fastf1_client.fastf1.get_session", return_value=session),
    ):
        records = get_session_laps(2024, 1, "R")

    session.load.assert_called_once_with(laps=True, telemetry=False, weather=False, messages=False)
    assert records == [{"Driver": "VER", "LapNumber": 1.0}]


def test_get_session_weather_requests_only_weather() -> None:
    weather = pd.DataFrame({"AirTemp": [24.5]})
    session = _mock_session(weather_data=weather)
    with (
        patch("collectors.fastf1_client.ensure_cache_enabled"),
        patch("collectors.fastf1_client.fastf1.get_session", return_value=session),
    ):
        records = get_session_weather(2024, 1, "R")

    session.load.assert_called_once_with(laps=False, telemetry=False, weather=True, messages=False)
    assert records == [{"AirTemp": 24.5}]


class TestErrorWrapping:
    """A FastF1-sourced failure must surface as this package's own
    `CollectorError` subclasses (not a raw `fastf1`/`requests` exception),
    so `main.py`'s `except CollectorError` isolates it from the rest of a
    `collect` run the same way it already does for `ergast_client.py`
    failures (Phase 7 audit, High) — except `InvalidSessionError`, which
    stays unwrapped on purpose (a caller error, not a source failure)."""

    def test_get_event_schedule_wraps_a_network_failure(self) -> None:
        with (
            patch("collectors.fastf1_client.ensure_cache_enabled"),
            patch(
                "collectors.fastf1_client.fastf1.get_event_schedule",
                side_effect=requests.ConnectionError("boom"),
            ),
            pytest.raises(SourceUnavailableError),
        ):
            get_event_schedule(2024)

    def test_get_session_results_wraps_a_rate_limit_error(self) -> None:
        with (
            patch("collectors.fastf1_client.ensure_cache_enabled"),
            patch(
                "collectors.fastf1_client.fastf1.get_session",
                side_effect=RateLimitExceededError(),
            ),
            pytest.raises(SourceUnavailableError),
        ):
            get_session_results(2024, 1, "R")

    def test_get_session_laps_wraps_no_lap_data_error(self) -> None:
        session = MagicMock()
        session.load.side_effect = NoLapDataError()
        with (
            patch("collectors.fastf1_client.ensure_cache_enabled"),
            patch("collectors.fastf1_client.fastf1.get_session", return_value=session),
            pytest.raises(UnexpectedResponseShapeError),
        ):
            get_session_laps(2024, 1, "R")

    def test_invalid_session_error_is_not_wrapped(self) -> None:
        with (
            patch("collectors.fastf1_client.ensure_cache_enabled"),
            patch(
                "collectors.fastf1_client.fastf1.get_session",
                side_effect=InvalidSessionError(),
            ),
            pytest.raises(InvalidSessionError),
        ):
            get_session_results(2024, 1, "R")
