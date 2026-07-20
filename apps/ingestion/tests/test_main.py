"""Unit tests for `main.py` — argument parsing, entity dispatch, and
`run_collect`'s per-entity partial-failure handling.

Before this file, none of this was tested at all: a test asserting "a
FastF1 collector exception during a mixed `--entities` run still processes
the remaining entities" would have caught the High-severity FastF1-error-
isolation bug directly (Phase 7 audit, Medium).
"""

from __future__ import annotations

import pytest
from pydantic import BaseModel

import main
from collectors.exceptions import SourceUnavailableError
from main import CollectArgs, CollectedBatch, TransformArgs, parse_args, run_collect


class _FakeRecord(BaseModel):
    id: int


def test_parse_args_collect_splits_and_strips_entities() -> None:
    args = parse_args(
        ["collect", "--season", "2024", "--entities", "fastf1-schedule, jolpica-calendar"]
    )

    assert isinstance(args, CollectArgs)
    assert args.season == 2024
    assert args.entities == ["fastf1-schedule", "jolpica-calendar"]
    assert args.dry_run is False


def test_parse_args_transform() -> None:
    args = parse_args(["transform", "--season", "2023"])

    assert isinstance(args, TransformArgs)
    assert args.season == 2023
    assert args.raw_database_url is None


def test_run_collect_returns_1_for_an_unknown_entity(monkeypatch: pytest.MonkeyPatch) -> None:
    args = CollectArgs(
        season=2024,
        round=None,
        session="R",
        entities=["not-a-real-entity"],
        dry_run=True,
        database_url=None,
    )

    assert run_collect(args) == 1


def test_run_collect_isolates_one_entitys_collector_failure_from_the_rest(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The exact regression the High-severity FastF1 finding described: one
    entity's `CollectorError` must not stop the remaining entities in the
    same `--entities` run."""

    def _ok_handler(args: CollectArgs) -> CollectedBatch:
        return CollectedBatch("test", _FakeRecord, [{"id": 1}], "id")

    def _broken_handler(args: CollectArgs) -> CollectedBatch:
        raise SourceUnavailableError("simulated source outage")

    monkeypatch.setitem(main.ENTITY_HANDLERS, "ok-entity", _ok_handler)
    monkeypatch.setitem(main.ENTITY_HANDLERS, "broken-entity", _broken_handler)

    args = CollectArgs(
        season=2024,
        round=None,
        session="R",
        entities=["broken-entity", "ok-entity"],
        dry_run=True,
        database_url=None,
    )

    exit_code = run_collect(args)

    assert exit_code == 1  # the broken entity's failure is still reported
    # ...but the ok entity after it was still collected and validated.
    assert "ok-entity: 1 valid, 0 rejected" in capsys.readouterr().out


def test_run_collect_returns_0_when_every_entity_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _ok_handler(args: CollectArgs) -> CollectedBatch:
        return CollectedBatch("test", _FakeRecord, [{"id": 1}], "id")

    monkeypatch.setitem(main.ENTITY_HANDLERS, "ok-entity", _ok_handler)

    args = CollectArgs(
        season=2024, round=None, session="R", entities=["ok-entity"], dry_run=True, database_url=None
    )

    assert run_collect(args) == 0
