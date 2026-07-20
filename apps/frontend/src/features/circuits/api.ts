import type {
  Circuit,
  CircuitRaceHistoryEntry,
  CircuitRecord,
} from "@pit-wall-insight/shared-types";

import { apiGet, apiGetCollection, type QueryParamValue } from "../../lib/api-client.js";

export interface ListCircuitsParams {
  page?: number;
  limit?: number;
  [key: string]: QueryParamValue;
}

/** `GET /circuits` (docs/08_API_SPECIFICATION.md — "Circuits"). */
export function listCircuits(params?: ListCircuitsParams): Promise<{ data: Circuit[] }> {
  return apiGetCollection<Circuit>("/circuits", params);
}

/** `GET /circuits/{id}`. */
export function getCircuit(circuitId: string): Promise<Circuit> {
  return apiGet<Circuit>(`/circuits/${circuitId}`);
}

/** `GET /circuits/{id}/history` — races run at this circuit, most recent first. */
export function getCircuitHistory(circuitId: string): Promise<CircuitRaceHistoryEntry[]> {
  return apiGet<CircuitRaceHistoryEntry[]>(`/circuits/${circuitId}/history`);
}

/** `GET /circuits/{id}/records` — fastest lap ever recorded here. */
export function getCircuitRecords(circuitId: string): Promise<CircuitRecord> {
  return apiGet<CircuitRecord>(`/circuits/${circuitId}/records`);
}
