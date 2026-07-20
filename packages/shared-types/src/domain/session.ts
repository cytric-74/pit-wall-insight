/**
 * `/sessions*` (docs/08_API_SPECIFICATION.md — "Sessions"). Mirrors
 * `apps/backend/app/schemas/session.py` exactly. There is no dedicated
 * Sessions page in the frontend — every one of these is composed by
 * other features (Races, Drivers, Constructors) that need a specific
 * session's results/laps, via `apps/frontend/src/features/sessions/`.
 */

export interface SessionMetadata {
  id: string;
  season: number;
  round: number;
  raceName: string | null;
  sessionType: string;
  circuit: string | null;
  date: string | null;
}

export interface SessionResultEntry {
  driver: string;
  team: string | null;
  gridPosition: number | null;
  finishPosition: number | null;
  points: number | null;
  status: string | null;
  fastestLap: boolean | null;
  lapsCompleted: number | null;
}

export interface SessionLapEntry {
  driver: string;
  lapNumber: number;
  lapTime: number | null;
  compound: string | null;
  tyreLife: number | null;
  position: number | null;
  pitIn: boolean | null;
  pitOut: boolean | null;
}
