import type { Driver, DriverCareerStatistics, DriverLap } from "@pit-wall-insight/shared-types";

import type { QueryParamValue } from "../../lib/api-client.js";
import { apiGet, apiGetCollection } from "../../lib/api-client.js";

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
}

/** `GET /drivers` (docs/08_API_SPECIFICATION.md — "Drivers"). */
export function listDrivers(params?: ListDriversParams): Promise<{ data: Driver[] }> {
  const { constructorId, ...rest } = params ?? {};
  return apiGetCollection<Driver>("/drivers", {
    ...(rest as Record<string, QueryParamValue>),
    constructor: constructorId,
  });
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
}

/** `GET /drivers/{id}/laps`. */
export function getDriverLaps(driverId: string, params?: DriverLapsParams): Promise<DriverLap[]> {
  return apiGet<DriverLap[]>(
    `/drivers/${driverId}/laps`,
    params as Record<string, QueryParamValue> | undefined,
  );
}
