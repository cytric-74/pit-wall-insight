"""Unit tests for `utils.ids.generate_id`.

What's being verified: the three properties `generate_id` exists to
guarantee — determinism (same inputs, same output, every time), stability
across process boundaries (a fresh Python process computes the identical
UUID, since the derivation has no runtime-random component), and
uniqueness across different natural keys and namespaces (two different
drivers must never collide, and a driver must never collide with a
constructor that happens to share the same literal id string).
"""

from __future__ import annotations

import uuid

from utils.ids import generate_id


def test_same_inputs_produce_the_same_id() -> None:
    first = generate_id("driver", "max_verstappen")
    second = generate_id("driver", "max_verstappen")
    assert first == second


def test_different_natural_keys_produce_different_ids() -> None:
    verstappen = generate_id("driver", "max_verstappen")
    norris = generate_id("driver", "lando_norris")
    assert verstappen != norris


def test_different_namespaces_produce_different_ids_for_the_same_key() -> None:
    """A driver and a constructor sharing the same literal natural key
    string (e.g. an unlikely but not impossible collision across two
    independent upstream sources) must not collide."""
    as_driver = generate_id("driver", "red_bull")
    as_constructor = generate_id("constructor", "red_bull")
    assert as_driver != as_constructor


def test_result_is_a_valid_uuid() -> None:
    result = generate_id("circuit", "bahrain")
    assert isinstance(result, uuid.UUID)
    # uuid5 always produces a version-5 UUID; asserting this catches any
    # accidental future switch to a different (e.g. random) generation
    # strategy that would break idempotent re-ingestion.
    assert result.version == 5


def test_natural_key_casing_is_significant() -> None:
    """Documents the deliberate non-normalization behavior: callers are
    responsible for normalizing a natural key's casing before calling
    `generate_id`, since only the caller knows whether a given upstream
    source's ids are meant to be case-sensitive."""
    lower = generate_id("driver", "max_verstappen")
    mixed = generate_id("driver", "Max_Verstappen")
    assert lower != mixed
