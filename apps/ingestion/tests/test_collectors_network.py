"""Opt-in tests that make one real call each to FastF1 and Jolpica-F1.

Purpose
-------
Every other test file in this suite mocks the network entirely, which
proves this module's *own* logic is correct but never proves the two
upstream APIs are actually reachable, still shaped the way this code
expects, or that FastF1's on-disk cache genuinely gets populated. This
file is the one place that makes real HTTP calls, to prove exactly that —
deliberately kept to the smallest possible real calls (one recent season's
schedule; one historical season's calendar) rather than anything slow.

Why these are excluded from the default run
--------------------------------------------
`pyproject.toml` registers the `network` marker and excludes it by default
(`addopts = ... -m "not network"`), matching this project's docs/06
distinction between fast unit tests and a separate, slower "Performance
Tests" bucket. Real network calls are slow and flaky in CI/offline
environments in a way unit tests must never be; running these requires an
explicit opt-in: `pytest -m network`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from collectors.ergast_client import get_season_calendar
from collectors.fastf1_client import get_event_schedule
from config.settings import get_settings

pytestmark = pytest.mark.network


def test_fastf1_event_schedule_is_reachable_and_populates_the_cache() -> None:
    records = get_event_schedule(2024)

    assert len(records) > 0
    assert {"RoundNumber", "EventName"}.issubset(records[0].keys())

    cache_dir = get_settings().fastf1_cache
    assert any(Path(cache_dir).iterdir()), "FastF1 cache directory is empty after a real call"


def test_jolpica_season_calendar_is_reachable() -> None:
    races = get_season_calendar(2023)

    assert len(races) > 0
    assert "raceName" in races[0]
    assert "Circuit" in races[0]
