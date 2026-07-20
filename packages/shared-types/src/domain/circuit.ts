/**
 * `/circuits*` (docs/08_API_SPECIFICATION.md — "Circuits"). Mirrors
 * `apps/backend/app/schemas/circuit.py` exactly. Notably absent:
 * `length`/`corners`/`drsZones`/`lapRecord`/`clockwise`/`svgTrack` — none
 * of these are collected anywhere in this pipeline
 * (apps/backend/app/models/gold/circuit.py documents why), so the backend
 * never serializes them.
 */

export interface Circuit {
  id: string;
  name: string;
  country: string | null;
  city: string | null;
  latitude: number | null;
  longitude: number | null;
}

export interface CircuitRaceHistoryEntry {
  season: number;
  round: number;
  raceName: string | null;
  winner: string | null;
  pole: string | null;
  fastestLap: string | null;
}

export interface CircuitRecord {
  driver: string | null;
  lapTime: number | null;
  season: number | null;
  round: number | null;
}
