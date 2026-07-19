"""Deterministic identifier generation.

Purpose
-------
`docs/07_DATABASE_SCHEMA.md` mandates UUID primary keys for every warehouse
table ("Decision 002: UUID Primary Keys — globally unique identifiers
improve scalability"). But every upstream source identifies things by a
natural key instead: FastF1 and Ergast/Jolpica both use short string ids
like `"max_verstappen"`, `"red_bull"`, `"bahrain"`. If a future loader phase
generated a *random* UUID (`uuid.uuid4`) for each of these on every run,
re-ingesting a season that was already loaded would create a brand-new row
for the same driver instead of updating the existing one — silently
breaking the idempotent "Incremental Loading" `docs/06_DATA_ENGINEERING.md`
requires.

The fix is to derive the UUID *from* the natural key, deterministically:
the same natural key must always produce the same UUID, on any machine, on
any run, forever. `uuid.uuid5` (name-based, deterministic UUIDs from a
namespace + name) is built for exactly this, unlike `uuid.uuid4` (random).

This module has no database dependency and isn't consumed by anything yet
in this phase — it's built now because it's a self-contained utility this
phase's scope explicitly covers, and because getting the id-generation
strategy right is a design decision the next phase (bronze persistence)
would otherwise have to make from scratch, with nothing to test it against
in isolation from the loader code that would use it.
"""

from __future__ import annotations

import uuid

# A fixed namespace for every identifier this project generates, derived
# deterministically from a project-identifying string. Using `uuid5` here
# (rather than a hardcoded literal UUID) means the derivation is
# self-evidently reproducible from source — anyone reading this module can
# see exactly how the namespace came to be, rather than trusting an opaque
# magic constant.
_PROJECT_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "pitwallinsight.dev")


def generate_id(namespace: str, natural_key: str) -> uuid.UUID:
    """Deterministically derive a UUID from an entity type and its natural key.

    Inputs:
        namespace: what *kind* of natural key this is (e.g. `"driver"`,
            `"constructor"`, `"circuit"`, `"season"`). Kept separate from
            `natural_key` so that two different entity types which happen
            to share the same literal natural-key string across two
            independent upstream sources (unlikely, but not structurally
            impossible) still resolve to different UUIDs.
        natural_key: the upstream source's own identifier string for this
            entity (e.g. FastF1/Ergast's `driverId` value).

    Outputs:
        A `uuid.UUID` that is stable across processes, machines, and time
        for the same (`namespace`, `natural_key`) pair — calling this again
        next season for the same driver returns the identical UUID.

    Edge case: this function does not normalize `natural_key` (casing,
    surrounding whitespace) — `generate_id("driver", "Max_Verstappen")` and
    `generate_id("driver", "max_verstappen")` deliberately produce different
    UUIDs, because only the caller knows whether a given upstream source's
    natural keys are meant to be treated case-sensitively. Callers that
    need normalization should normalize before calling this function, not
    after.

    Time complexity: O(len(natural_key)) — `uuid5` hashes its input
    (SHA-1 internally); there is no way to derive a deterministic UUID in
    less time than reading the input once.
    """
    return uuid.uuid5(_PROJECT_NAMESPACE, f"{namespace}:{natural_key}")
