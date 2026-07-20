import { useQuery } from "@tanstack/react-query";

import {
  compareConstructors,
  compareDrivers,
  compareRaces,
  type CompareConstructorsParams,
  type CompareDriversParams,
  type CompareRacesParams,
} from "./api.js";

export const compareKeys = {
  all: ["compare"] as const,
  drivers: (params: CompareDriversParams) => [...compareKeys.all, "drivers", params] as const,
  constructors: (params: CompareConstructorsParams) =>
    [...compareKeys.all, "constructors", params] as const,
  races: (params: CompareRacesParams) => [...compareKeys.all, "races", params] as const,
};

export function useCompareDrivers(params: CompareDriversParams | undefined) {
  return useQuery({
    queryKey: compareKeys.drivers(params ?? { driverA: "", driverB: "" }),
    queryFn: () => compareDrivers(params!),
    enabled: params !== undefined,
  });
}

export function useCompareConstructors(params: CompareConstructorsParams | undefined) {
  return useQuery({
    queryKey: compareKeys.constructors(params ?? { constructorA: "", constructorB: "" }),
    queryFn: () => compareConstructors(params!),
    enabled: params !== undefined,
  });
}

export function useCompareRaces(params: CompareRacesParams | undefined) {
  return useQuery({
    queryKey: compareKeys.races(params ?? { raceA: "", raceB: "" }),
    queryFn: () => compareRaces(params!),
    enabled: params !== undefined,
  });
}
