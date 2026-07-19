"""Runtime table reflection and dialect-aware upsert — shared by `loaders/` and `transformers/`.

Purpose
-------
Both `loaders/bronze_loader.py` (raw/Bronze API calls -> Bronze tables) and
`transformers/bronze_to_gold.py` (Bronze tables -> Gold tables) need to
write into tables whose SQLAlchemy models live in `apps/backend`, without
importing that package (see `loaders/bronze_loader.py`'s module docstring
for the full "no cross-app import" rationale — reflecting a table's
structure from the live database at runtime is the alternative). Factoring
the reflect-with-UUID-override and dialect-aware-upsert logic out here,
rather than duplicating it in both modules, is what keeps that logic
correct in exactly one place.

Inputs / Outputs: see each function's own docstring.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import Column, MetaData, Table, func
from sqlalchemy.engine import Engine


def reflect_table(engine: Engine, name: str, *uuid_columns: Column[Any]) -> Table:
    """Reflect a table's structure from the live database, overriding specific columns' types.

    Inputs: `name` — the table to reflect. `uuid_columns` — explicit
    `Column("some_id", Uuid(), ...)` objects for every UUID-typed column
    this caller will read or write (typically the primary key and any
    foreign keys) — SQLAlchemy prefers explicitly-passed columns over
    reflected ones of the same name, which is the mechanism this relies on.

    Why this override exists: PostgreSQL has a native `UUID` column type
    that reflects back as a UUID-aware SQLAlchemy type automatically, but
    SQLite (used only in this project's tests, since there's no Postgres
    available in this environment) has no native UUID type, so a column
    created via SQLAlchemy's portable `Uuid()` type reflects back from
    SQLite as a plain `CHAR`/`TEXT` column — losing the Python-level UUID
    (de)serialization only the original `Uuid()` type object provides.
    Passing every UUID column explicitly keeps both dialects' reflected
    tables behaving identically from Python's point of view.

    A fresh `MetaData()` is used per call (rather than one shared
    instance) so repeated calls for the same table name within one process
    can never collide with an already-registered `Table` of that name.
    """
    metadata = MetaData()
    return Table(name, metadata, *uuid_columns, autoload_with=engine)


def upsert(
    engine: Engine,
    table: Table,
    rows: list[dict[str, Any]],
    conflict_columns: list[str],
    *,
    update_columns: list[str] | None = None,
) -> int:
    """Insert `rows` into `table`, updating in place on a natural-key conflict.

    Inputs: `rows` — plain dicts keyed by column name (must include every
    non-audit column the target table expects; `created_at`/`updated_at`
    are deliberately omitted here — see below). `conflict_columns` — the
    column names forming the table's natural-key unique constraint.
    `update_columns` — restrict which columns get overwritten on conflict
    to exactly this list (`updated_at` is always included regardless).
    `None` (the default) updates every column the row data provides except
    the primary key, `created_at`, and the conflict columns themselves —
    the right default for straightforward Bronze upserts, where a row's
    entire content should always reflect its latest fetch.

    Some Gold-layer rows don't fit that default: `dim_season`'s
    `champion_driver`/`champion_constructor` and `dim_driver`'s
    `world_titles` are populated by a separate *finalize* step that runs
    later in the same transform pass (see
    `transformers/bronze_to_gold.py`), after the row this function creates
    already exists. Without `update_columns` narrowing what a later,
    unrelated re-upsert of the same row is allowed to touch, re-running the
    earlier "shell" step would silently wipe out the finalize step's work
    back to `NULL` on every subsequent pipeline run.

    Outputs: the number of rows submitted (not necessarily the number of
    *new* rows created, since some may have updated an existing row).

    Time complexity: O(1) round trip regardless of `len(rows)` — every row
    is submitted in a single multi-row `INSERT`, not one statement per row.
    """
    if not rows:
        return 0

    # `postgresql.insert` and `sqlite.insert` return dialect-specific
    # `Insert` subclasses with incompatible static types (mypy cannot unify
    # them under one local name), even though both expose an identical
    # `.on_conflict_do_update(...)` API at runtime — hence `Any` here
    # rather than a precise type for `dialect_insert`/`statement`.
    dialect = engine.dialect.name
    dialect_insert: Any
    if dialect == "postgresql":
        from sqlalchemy.dialects.postgresql import insert as dialect_insert
    elif dialect == "sqlite":
        from sqlalchemy.dialects.sqlite import insert as dialect_insert
    else:
        raise NotImplementedError(
            f"upsert is only implemented for postgresql and sqlite, got {dialect!r}"
        )

    statement = dialect_insert(table).values(rows)

    if update_columns is not None:
        update_values: dict[str, Any] = {
            column_name: statement.excluded[column_name] for column_name in update_columns
        }
    else:
        # The primary key (whatever it's actually named — `id` on Bronze
        # tables, `driver_id`/`season_id`/etc. on Gold ones) must never
        # appear in the UPDATE SET clause, alongside `created_at` (set once,
        # at insert, never again) and the natural-key columns driving the
        # conflict itself (redundant to re-set, since they're equal
        # already).
        never_update = {
            *(column.name for column in table.primary_key.columns),
            "created_at",
            *conflict_columns,
        }
        update_values = {
            column.name: column
            for column in statement.excluded
            if column.name not in never_update
        }

    # `updated_at` is deliberately re-assigned here even though it may
    # already be present above (mapped to `excluded.updated_at`, i.e.
    # whatever NULL/default the INSERT side would have produced, since
    # callers never pass it themselves) — this explicit assignment is what
    # actually bumps it to "now" on conflict.
    update_values["updated_at"] = func.now()
    statement = statement.on_conflict_do_update(
        index_elements=conflict_columns, set_=update_values
    )

    with engine.begin() as connection:
        connection.execute(statement)
    return len(rows)
