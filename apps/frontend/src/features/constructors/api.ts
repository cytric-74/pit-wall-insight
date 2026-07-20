import type {
  Constructor,
  ConstructorCareerStatistics,
  ConstructorSeasonSummary,
  Driver,
} from "@pit-wall-insight/shared-types";

import type { QueryParamValue } from "../../lib/api-client.js";
import { apiGet, apiGetCollection } from "../../lib/api-client.js";

export interface ListConstructorsParams {
  page?: number;
  limit?: number;
}

/** `GET /constructors` (docs/08_API_SPECIFICATION.md — "Constructors"). */
export function listConstructors(
  params?: ListConstructorsParams,
): Promise<{ data: Constructor[] }> {
  return apiGetCollection<Constructor>(
    "/constructors",
    params as Record<string, QueryParamValue> | undefined,
  );
}

/** `GET /constructors/{id}`. */
export function getConstructor(constructorId: string): Promise<Constructor> {
  return apiGet<Constructor>(`/constructors/${constructorId}`);
}

/** `GET /constructors/{id}/drivers` — the current roster. Also used by the
 * Drivers feature to find a driver's teammate. */
export function getConstructorDrivers(constructorId: string): Promise<Driver[]> {
  return apiGet<Driver[]>(`/constructors/${constructorId}/drivers`);
}

/** `GET /constructors/{id}/statistics`. */
export function getConstructorStatistics(
  constructorId: string,
): Promise<ConstructorCareerStatistics> {
  return apiGet<ConstructorCareerStatistics>(`/constructors/${constructorId}/statistics`);
}

/** `GET /constructors/{id}/performance` — one entry per season loaded. */
export function getConstructorPerformance(
  constructorId: string,
): Promise<ConstructorSeasonSummary[]> {
  return apiGet<ConstructorSeasonSummary[]>(`/constructors/${constructorId}/performance`);
}
