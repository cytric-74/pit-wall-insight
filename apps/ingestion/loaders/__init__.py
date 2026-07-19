"""Loaders — the only ingestion layer allowed to write to the raw/bronze database.

docs/06_DATA_ENGINEERING.md's contract for this layer: "Loading validated
datasets into PostgreSQL. Never perform analytics." Every function in
`bronze_loader.py` takes already-validated records (Pydantic model
instances produced by `validators/validate.py`) and writes them; none of
them compute a statistic, aggregate anything, or decide which of two
sources' data is "more correct" — that's Gold-layer transformation, a
future phase.
"""
