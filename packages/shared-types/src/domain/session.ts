/**
 * `/sessions*` (docs/08_API_SPECIFICATION.md — "Sessions"). Only
 * `SessionResultEntry` is defined here so far, for the same reason as
 * `race.ts` — `SessionMetadata`/`SessionLapEntry` get added when the
 * dedicated Sessions feature is migrated.
 */

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
