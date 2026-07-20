import type {
  ConstructorComparison,
  DriverComparison,
  RaceComparison,
} from "@pit-wall-insight/shared-types";

import { apiGet } from "../../lib/api-client.js";

/**
 * `/compare/*` (docs/08_API_SPECIFICATION.md — "Comparison"). No dedicated
 * Comparison page exists in the frontend yet — this formalizes the API
 * surface (types, fetch functions, query hooks) so a future page (or
 * another feature that wants a side-by-side view) doesn't have to build
 * it from scratch.
 */

export interface CompareDriversParams {
  driverA: string;
  driverB: string;
  season?: number;
}

/** `GET /compare/drivers`. Equivalent to `/drivers/{id}/comparison/{otherId}`
 * (docs/08 lists both routes for the same comparison). */
export function compareDrivers(params: CompareDriversParams): Promise<DriverComparison> {
  return apiGet<DriverComparison>("/compare/drivers", {
    driverA: params.driverA,
    driverB: params.driverB,
    season: params.season,
  });
}

export interface CompareConstructorsParams {
  constructorA: string;
  constructorB: string;
  season?: number;
}

/** `GET /compare/constructors`. */
export function compareConstructors(
  params: CompareConstructorsParams,
): Promise<ConstructorComparison> {
  return apiGet<ConstructorComparison>("/compare/constructors", {
    constructorA: params.constructorA,
    constructorB: params.constructorB,
    season: params.season,
  });
}

export interface CompareRacesParams {
  raceA: string;
  raceB: string;
}

/** `GET /compare/races`. */
export function compareRaces(params: CompareRacesParams): Promise<RaceComparison> {
  return apiGet<RaceComparison>("/compare/races", { raceA: params.raceA, raceB: params.raceB });
}
