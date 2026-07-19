"""Pydantic models describing the shape of each raw record this pipeline collects.

Purpose
-------
Each model here mirrors one collector function's output *exactly as the
source names it* — FastF1's PascalCase columns (`RoundNumber`, `LapTime`),
Ergast/Jolpica's camelCase fields (`driverId`, `positionText`) — rather than
renaming anything to this project's own conventions. That renaming (to the
`raw_*` table column names in `docs/07_DATABASE_SCHEMA.md`, and later to
`stg_*` standardized names) is staging/transformation work for a future
phase; docs/06_DATA_ENGINEERING.md is explicit that the Bronze layer is
"minimal transformation, source aligned." Validating against the source's
own shape — instead of an already-renamed one — also means a validation
failure message points directly at the field name the source actually sent,
which is what someone debugging a pipeline failure needs to see.

Every field that isn't required to identify or classify a record is
`Optional` with a default, because Formula One's own data is genuinely
incomplete in ordinary, expected ways (a retired driver has no
`Sector3Time` on their last lap; a session with no rain has `Rainfall`
but a driver disqualified post-race has no `points`). Modeling those as
required would turn *normal* F1 data into validation failures.

Inputs
------
None directly — these are data shape declarations, not functions.

Outputs
-------
None directly — consumed by `validators/validate.py`, which calls
`Model.model_validate(record)` for each raw record a collector produced.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _RawRecord(BaseModel):
    """Shared configuration for every raw-record model in this module.

    `extra="ignore"` matters here specifically: FastF1 and Ergast both add
    new fields to their responses over time (e.g. FastF1 has added new lap
    columns across releases), and this pipeline should not treat "the
    source sent us a field we don't model yet" as a validation failure —
    only "the source is missing a field we need, or sent the wrong type
    for one" should be.
    """

    model_config = ConfigDict(extra="ignore")


# ---------------------------------------------------------------------------
# FastF1-sourced shapes
# ---------------------------------------------------------------------------


class RawEventSchedule(_RawRecord):
    """One row of `fastf1_client.get_event_schedule` — one race weekend.

    `F1ApiSupport` is the single most important field for downstream code:
    it tells a future loader phase whether session-level data
    (results/laps/weather) can be expected to exist for this event at all.
    """

    RoundNumber: int
    EventName: str
    Country: str
    Location: str
    EventDate: str | None = None
    EventFormat: str | None = None
    F1ApiSupport: bool = False


class RawSessionResult(_RawRecord):
    """One row of `fastf1_client.get_session_results` — one driver's classification.

    `Position` is `None` for a driver who was not classified (e.g. did not
    start) — a real, expected outcome, not missing data.
    """

    DriverNumber: str
    Abbreviation: str
    TeamName: str
    Position: float | None = None
    GridPosition: float | None = None
    Points: float = 0.0
    Status: str | None = None
    Time: float | None = None
    Q1: float | None = None
    Q2: float | None = None
    Q3: float | None = None


class RawSessionLap(_RawRecord):
    """One row of `fastf1_client.get_session_laps` — one driver's one lap.

    `PitInTime`/`PitOutTime` being non-`None` together identifies a pit
    stop lap — a future transformer derives `fct_pitstop` from exactly this
    signal rather than a separate source, since none exists.
    """

    Driver: str
    LapNumber: float
    LapTime: float | None = None
    Sector1Time: float | None = None
    Sector2Time: float | None = None
    Sector3Time: float | None = None
    Compound: str | None = None
    TyreLife: float | None = None
    Stint: float | None = None
    PitInTime: float | None = None
    PitOutTime: float | None = None
    Position: float | None = None


class RawWeatherSample(_RawRecord):
    """One row of `fastf1_client.get_session_weather` — one timestamped weather reading."""

    Time: float
    AirTemp: float
    TrackTemp: float
    Humidity: float
    Pressure: float
    Rainfall: bool
    WindDirection: float
    WindSpeed: float


# ---------------------------------------------------------------------------
# Jolpica-F1 (Ergast-compatible) sourced shapes
# ---------------------------------------------------------------------------


class RawLocation(_RawRecord):
    """Nested `Circuit.Location` object inside an Ergast/Jolpica calendar entry."""

    lat: str
    long: str
    locality: str
    country: str


class RawCircuitRef(_RawRecord):
    """Nested `Circuit` object inside an Ergast/Jolpica calendar entry."""

    circuitId: str
    circuitName: str
    Location: RawLocation


class RawRaceCalendarEntry(_RawRecord):
    """One row of `ergast_client.get_season_calendar` — one round of a season."""

    season: str
    round: str
    raceName: str
    date: str
    time: str | None = None
    Circuit: RawCircuitRef


class RawDriverRef(_RawRecord):
    """Nested `Driver` object shared by standings and results responses.

    `code` (the 3-letter abbreviation FastF1 also uses, e.g. `"VER"`) is
    `None` for many pre-2014 drivers — Ergast only started assigning driver
    codes once F1 broadcasts started showing them consistently.
    """

    driverId: str
    code: str | None = None
    givenName: str
    familyName: str
    dateOfBirth: str
    nationality: str


class RawConstructorRef(_RawRecord):
    """Nested `Constructor` object shared by standings and results responses."""

    constructorId: str
    name: str
    nationality: str


class RawDriverStanding(_RawRecord):
    """One row of `ergast_client.get_driver_standings` — one driver's season standing."""

    position: str
    points: str
    wins: str
    Driver: RawDriverRef
    Constructors: list[RawConstructorRef]


class RawConstructorStanding(_RawRecord):
    """One row of `ergast_client.get_constructor_standings` — one constructor's season standing."""

    position: str
    points: str
    wins: str
    Constructor: RawConstructorRef


class RawRaceResult(_RawRecord):
    """One row of `ergast_client.get_race_results` — one driver's classification in one race.

    `status` is free text from Ergast (`"Finished"`, `"+1 Lap"`,
    `"Retired"`, `"Accident"`, ...) rather than an enum — Ergast has
    accumulated dozens of distinct status strings across F1 history, and
    normalizing them into a fixed set is staging-layer work, not
    validation.
    """

    number: str
    position: str
    positionText: str
    points: str
    grid: str
    laps: str
    status: str
    Driver: RawDriverRef
    Constructor: RawConstructorRef
