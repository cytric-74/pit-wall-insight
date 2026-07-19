"""Small, dependency-free helpers shared across the ingestion pipeline.

Everything here is a pure function or a stateless-per-instance utility with
no knowledge of FastF1, Ergast, or any future database layer — that's what
keeps them usable from every phase of this pipeline (this one and future
ones) without creating import cycles back into `collectors/` or `validators/`.
"""
