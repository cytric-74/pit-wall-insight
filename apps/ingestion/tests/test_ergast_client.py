"""Unit tests for `collectors.ergast_client`.

No network access happens in this file — every HTTP call is mocked, so
these tests verify this module's own logic (envelope unwrapping,
pagination, and error classification) rather than Jolpica-F1's live
behavior. Real connectivity is covered separately by
`test_collectors_network.py`, marked `@pytest.mark.network` and excluded
from this default run.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

import collectors.ergast_client as ergast_client
from collectors.ergast_client import (
    _extract_list,
    _get,
    _get_paginated,
    get_constructor_standings,
    get_driver_standings,
    get_race_results,
    get_season_calendar,
)
from collectors.exceptions import SourceUnavailableError, UnexpectedResponseShapeError


@pytest.fixture(autouse=True)
def _reset_response_cache() -> None:
    """Reset the module-level in-process response cache before every test
    in this file — several tests call `_get("2024.json")` with different
    mocked bodies, and without this the cache would leak the first test's
    response into the next (Phase 7 audit, Medium: added alongside the
    cache itself)."""
    ergast_client._response_cache.clear()


def _mock_settings() -> MagicMock:
    return MagicMock(
        jolpica_base_url="https://api.jolpi.ca/ergast/f1",
        user_agent="test-agent/1.0",
        request_timeout_seconds=5.0,
    )


class TestGet:
    def test_raises_source_unavailable_on_connection_error(self) -> None:
        with (
            patch("collectors.ergast_client.get_settings", return_value=_mock_settings()),
            patch("collectors.ergast_client.requests.get", side_effect=requests.ConnectionError),
            pytest.raises(SourceUnavailableError),
        ):
            _get("2024.json")

    def test_raises_source_unavailable_on_http_error_status(self) -> None:
        response = MagicMock()
        response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        with (
            patch("collectors.ergast_client.get_settings", return_value=_mock_settings()),
            patch("collectors.ergast_client.requests.get", return_value=response),
            pytest.raises(SourceUnavailableError),
        ):
            _get("2024.json")

    def test_sends_configured_user_agent_and_timeout(self) -> None:
        response = MagicMock()
        response.json.return_value = {"MRData": {}}
        with (
            patch("collectors.ergast_client.get_settings", return_value=_mock_settings()),
            patch("collectors.ergast_client.requests.get", return_value=response) as mock_get,
        ):
            _get("2024.json", params={"limit": 100, "offset": 0})

        _, kwargs = mock_get.call_args
        assert kwargs["headers"] == {"User-Agent": "test-agent/1.0"}
        assert kwargs["timeout"] == 5.0
        assert kwargs["params"] == {"limit": 100, "offset": 0}

    def test_repeating_an_identical_call_hits_the_cache_not_the_network(self) -> None:
        response = MagicMock()
        response.json.return_value = {"MRData": {"total": "0"}}
        with (
            patch("collectors.ergast_client.get_settings", return_value=_mock_settings()),
            patch("collectors.ergast_client.requests.get", return_value=response) as mock_get,
        ):
            first = _get("2024/driverStandings.json", params={"limit": 100, "offset": 0})
            second = _get("2024/driverStandings.json", params={"limit": 100, "offset": 0})

        assert first == second
        mock_get.assert_called_once()

    def test_a_different_path_is_not_served_from_another_paths_cache_entry(self) -> None:
        response = MagicMock()
        response.json.return_value = {"MRData": {"total": "0"}}
        with (
            patch("collectors.ergast_client.get_settings", return_value=_mock_settings()),
            patch("collectors.ergast_client.requests.get", return_value=response) as mock_get,
        ):
            _get("2024.json")
            _get("2023.json")

        assert mock_get.call_count == 2


class TestExtractList:
    def test_returns_items_and_total(self) -> None:
        payload = {"MRData": {"total": "2", "RaceTable": {"Races": [{"round": "1"}, {"round": "2"}]}}}
        items, total = _extract_list(payload, "RaceTable", "Races")
        assert items == [{"round": "1"}, {"round": "2"}]
        assert total == 2

    def test_empty_list_is_valid_not_an_error(self) -> None:
        payload = {"MRData": {"total": "0", "RaceTable": {"Races": []}}}
        items, total = _extract_list(payload, "RaceTable", "Races")
        assert items == []
        assert total == 0

    def test_raises_when_mrdata_is_missing(self) -> None:
        with pytest.raises(UnexpectedResponseShapeError):
            _extract_list({}, "RaceTable", "Races")

    def test_raises_when_an_intermediate_key_is_missing(self) -> None:
        payload = {"MRData": {"total": "0"}}
        with pytest.raises(UnexpectedResponseShapeError):
            _extract_list(payload, "RaceTable", "Races")

    def test_raises_when_the_resolved_node_is_not_a_list(self) -> None:
        payload = {"MRData": {"total": "1", "RaceTable": {"Races": "not-a-list"}}}
        with pytest.raises(UnexpectedResponseShapeError):
            _extract_list(payload, "RaceTable", "Races")


class TestGetPaginated:
    def test_combines_multiple_pages(self) -> None:
        page_one = {
            "MRData": {"total": "3", "RaceTable": {"Races": [{"round": "1"}, {"round": "2"}]}}
        }
        page_two = {"MRData": {"total": "3", "RaceTable": {"Races": [{"round": "3"}]}}}
        with patch(
            "collectors.ergast_client._get", side_effect=[page_one, page_two]
        ) as mock_get:
            result = _get_paginated("2024.json", "RaceTable", "Races")

        assert result == [{"round": "1"}, {"round": "2"}, {"round": "3"}]
        assert mock_get.call_count == 2

    def test_stops_after_a_single_page_when_total_is_zero(self) -> None:
        empty_page = {"MRData": {"total": "0", "RaceTable": {"Races": []}}}
        with patch("collectors.ergast_client._get", return_value=empty_page) as mock_get:
            result = _get_paginated("2099.json", "RaceTable", "Races")

        assert result == []
        mock_get.assert_called_once()


def _standings_payload(list_key: str, items: list[dict[str, object]]) -> dict[str, object]:
    return {
        "MRData": {
            "total": str(len(items)),
            "StandingsTable": {"StandingsLists": [{list_key: items}]},
        }
    }


class TestPublicFunctions:
    def test_get_season_calendar_returns_races(self) -> None:
        payload = {
            "MRData": {"total": "1", "RaceTable": {"Races": [{"round": "1", "raceName": "Bahrain Grand Prix"}]}}
        }
        with patch("collectors.ergast_client._get", return_value=payload):
            races = get_season_calendar(2024)
        assert races == [{"round": "1", "raceName": "Bahrain Grand Prix"}]

    def test_get_driver_standings_returns_the_nested_list(self) -> None:
        payload = _standings_payload("DriverStandings", [{"position": "1", "points": "575"}])
        with patch("collectors.ergast_client._get", return_value=payload):
            standings = get_driver_standings(2023)
        assert standings == [{"position": "1", "points": "575"}]

    def test_get_driver_standings_returns_empty_list_when_no_standings_yet(self) -> None:
        payload = {"MRData": {"total": "0", "StandingsTable": {"StandingsLists": []}}}
        with patch("collectors.ergast_client._get", return_value=payload):
            standings = get_driver_standings(2099)
        assert standings == []

    def test_get_constructor_standings_returns_the_nested_list(self) -> None:
        payload = _standings_payload("ConstructorStandings", [{"position": "1", "points": "860"}])
        with patch("collectors.ergast_client._get", return_value=payload):
            standings = get_constructor_standings(2023)
        assert standings == [{"position": "1", "points": "860"}]

    def test_get_race_results_returns_results(self) -> None:
        payload = {
            "MRData": {
                "total": "1",
                "RaceTable": {"Races": [{"Results": [{"position": "1", "points": "25"}]}]},
            }
        }
        with patch("collectors.ergast_client._get", return_value=payload):
            results = get_race_results(2024, 1)
        assert results == [{"position": "1", "points": "25"}]

    def test_get_race_results_returns_empty_list_for_a_nonexistent_round(self) -> None:
        payload = {"MRData": {"total": "0", "RaceTable": {"Races": []}}}
        with patch("collectors.ergast_client._get", return_value=payload):
            results = get_race_results(2024, 30)
        assert results == []
