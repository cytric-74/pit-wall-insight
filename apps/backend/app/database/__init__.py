"""Database engine, session factory, and declarative base.

This package owns connection setup only. It has no knowledge of FastAPI —
`app/dependencies/database.py` is what exposes a session as an injectable
dependency.
"""
