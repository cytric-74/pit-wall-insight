import type {
  Driver,
  DriverCareerStatistics,
  DriverLap,
  RaceListItem,
  SessionResultEntry,
} from "@pit-wall-insight/shared-types";

import { apiGet, apiGetCollection, type QueryParamValue } from "../../lib/api-client.js";

export interface ListDriversParams {
  season?: number;
  /** Sent as the `constructor` query parameter — named `constructorId`
   * here instead, since a plain object typed `{ constructor?: string }`
   * collides with every object's inherited `Object.prototype.constructor`. */
  constructorId?: string;
  nationality?: string;
  active?: boolean;
  sort?: string;
  page?: number;
  limit?: number;
  [key: string]: QueryParamValue;
}

/** `GET /drivers` (docs/08_API_SPECIFICATION.md — "Drivers"). */
export function listDrivers(params?: ListDriversParams): Promise<{ data: Driver[] }> {
  const { constructorId, ...rest } = params ?? {};
  return apiGetCollection<Driver>("/drivers", { ...rest, constructor: constructorId });
}

/** `GET /drivers/{id}`. */
export function getDriver(driverId: string): Promise<Driver> {
  return apiGet<Driver>(`/drivers/${driverId}`);
}

/** `GET /drivers/{id}/statistics`. */
export function getDriverStatistics(driverId: string): Promise<DriverCareerStatistics> {
  return apiGet<DriverCareerStatistics>(`/drivers/${driverId}/statistics`);
}

export interface DriverLapsParams {
  season?: number;
  race?: number;
  session?: string;
  compound?: string;
  [key: string]: QueryParamValue;
}

/** `GET /drivers/{id}/laps`. */
export function getDriverLaps(driverId: string, params?: DriverLapsParams): Promise<DriverLap[]> {
  return apiGet<DriverLap[]>(`/drivers/${driverId}/laps`, params);
}

/**
 * `GET /constructors/{id}/drivers` — used here to find a driver's current
 * teammate. The dedicated Constructors feature will build its own richer
 * `features/constructors/api.ts`; this is a narrow, Drivers-feature-local
 * use of the same endpoint.
 */
export function getConstructorDrivers(constructorId: string): Promise<Driver[]> {
  return apiGet<Driver[]>(`/constructors/${constructorId}/drivers`);
}

/**
 * The current season's races, in round order — built from `GET /races`
 * (no dedicated "current season" endpoint exists) by taking the most
 * recent season present in the (season desc, round desc)-ordered list.
 * Used here to reconstruct a driver's round-by-round grid/finish position
 * history, which no single endpoint exposes directly. The dedicated Races
 * feature will build its own richer API module later.
 */
export async function getCurrentSeasonRaces(): Promise<RaceListItem[]> {
  const { data } = await apiGetCollection<RaceListItem>("/races", { limit: 30 });
  if (data.length === 0) return [];
  const currentSeason = data[0]!.season;
  return data.filter((race) => race.season === currentSeason).sort((a, b) => a.round - b.round);
}

/** `GET /sessions/{id}/results` — see `getCurrentSeasonRaces` above. */
export function getSessionResults(sessionId: string): Promise<SessionResultEntry[]> {
  return apiGet<SessionResultEntry[]>(`/sessions/${sessionId}/results`);
}
