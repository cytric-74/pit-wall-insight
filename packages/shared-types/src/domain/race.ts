/**
 * `/races*` (docs/08_API_SPECIFICATION.md — "Races"). Mirrors
 * `apps/backend/app/schemas/race.py` exactly. A "race" is a
 * `dim_session` row scoped to `session_type == "R"` — not a separate
 * Gold entity — so `RaceListItem.id`/`RaceSummary.id` are the same
 * `session_id` UUIDs `/sessions/{id}` uses.
 *
 * `RaceWeather` is a single per-session snapshot, not a time series:
 * docs/08 calls this "weather evolution", but `dim_weather` is
 * deliberately one aggregated row per session — there is no
 * FastF1-sample-level time series retained past the Gold transform.
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

export interface RaceSummary {
  id: string;
  season: number;
  round: number;
  raceName: string | null;
  circuit: string | null;
  country: string | null;
  date: string | null;
  winner: string | null;
  pole: string | null;
  fastestLap: string | null;
  retirements: number | null;
  weather: string | null;
  averagePitstop: number | null;
}

export interface PositionEntry {
  driver: string;
  lapNumber: number;
  position: number | null;
}

export interface PitstopEntry {
  driver: string;
  lap: number;
  pitDuration: number | null;
  stopNumber: number | null;
  compoundBefore: string | null;
  compoundAfter: string | null;
}

export interface RaceWeather {
  airTemperature: number | null;
  trackTemperature: number | null;
  humidity: number | null;
  windSpeed: number | null;
  windDirection: number | null;
  rainfall: boolean | null;
  pressure: number | null;
}

export interface TyreStint {
  compound: string | null;
  startLap: number;
  endLap: number;
  lapCount: number;
}

export interface DriverStrategy {
  driver: string;
  stints: TyreStint[];
}
