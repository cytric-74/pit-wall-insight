/**
 * `/races*` (docs/08_API_SPECIFICATION.md — "Races"). Only `RaceListItem` is
 * defined here so far — added early because the Drivers feature composes
 * it (season race calendar) for its per-round position charts; the rest of
 * `apps/backend/app/schemas/race.py`'s shapes (`RaceSummary`,
 * `PositionEntry`, `PitstopEntry`, `RaceWeather`, `DriverStrategy`) get
 * added when the dedicated Races feature is migrated.
 */

export interface RaceListItem {
  id: string;
  season: number;
  round: number;
  raceName: string | null;
  circuit: string | null;
  country: string | null;
  date: string | null;
  winner: string | null;
}
