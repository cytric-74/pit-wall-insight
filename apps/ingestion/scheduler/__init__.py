"""Pipeline automation — intentionally unimplemented in this phase.

`docs/06_DATA_ENGINEERING.md` lists scheduling under "Future automation":
a daily refresh, race-weekend refresh, historical sync, and incremental
updates, initially run via GitHub Actions and later migrated to Apache
Airflow. None of that exists yet because there is nothing to schedule yet —
this phase (ingestion foundation) has no loaders or persistence, so a
scheduler would have nothing meaningful to trigger beyond what `main.py`
already does manually via its CLI.

This module exists only so the package structure matches
`docs/06_DATA_ENGINEERING.md`'s documented `apps/ingestion/` layout exactly.
It intentionally contains no functions, classes, or stub implementations —
per the phased build plan, a placeholder that pretends to schedule
something would be worse than no module at all, since it would look
functional without being connected to anything. A real scheduler (a GitHub
Actions workflow invoking `main.py`, or later an Airflow DAG) is future
work, once there's a loader/transform pipeline worth automating.
"""
