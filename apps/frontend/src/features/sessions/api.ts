import type {
  SessionLapEntry,
  SessionMetadata,
  SessionResultEntry,
} from "@pit-wall-insight/shared-types";

import { apiGet } from "../../lib/api-client.js";

/**
 * `/sessions*` (docs/08_API_SPECIFICATION.md — "Sessions"). No dedicated
 * Sessions page exists in the frontend — these are composed by Races
 * (a race session's results/positions), Drivers (per-round grid/finish
 * history), and Constructors (round-by-round team/driver points).
 */

/** `GET /sessions/{id}`. */
export function getSession(sessionId: string): Promise<SessionMetadata> {
  return apiGet<SessionMetadata>(`/sessions/${sessionId}`);
}

/** `GET /sessions/{id}/results`. */
export function getSessionResults(sessionId: string): Promise<SessionResultEntry[]> {
  return apiGet<SessionResultEntry[]>(`/sessions/${sessionId}/results`);
}

/** `GET /sessions/{id}/laps`. */
export function getSessionLaps(sessionId: string): Promise<SessionLapEntry[]> {
  return apiGet<SessionLapEntry[]>(`/sessions/${sessionId}/laps`);
}
