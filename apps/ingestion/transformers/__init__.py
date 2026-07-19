"""Bronze -> Gold transformation (docs/06_DATA_ENGINEERING.md).

This is where FastF1 and Jolpica-F1 rows for the "same" real-world entity
finally get reconciled into one row — the opposite of `loaders/`, which
keeps every source's rows separate (see `loaders/bronze_loader.py`'s
module docstring). Everything here reads from the raw/Bronze database and
writes to the analytics/Gold database — two different physical databases,
reflected at runtime the same "no cross-app import" way `loaders/` reads
and writes Bronze (see `utils/db.py`).

Per docs/06_DATA_ENGINEERING.md's Engineering Decisions, this transform is
implemented as ordinary Python/SQLAlchemy service code rather than dbt
models — there's no live Postgres/dbt runtime in this environment to
develop and validate an actual dbt project against, and the Gold table
shapes this produces are designed to match what dbt marts would eventually
produce, so migrating to dbt later doesn't change the schema, only how the
rows get there.
"""
