import { useQuery } from "@tanstack/react-query";

import {
  getConstructor,
  getConstructorDrivers,
  getConstructorPerformance,
  getConstructorStatistics,
  listConstructors,
  type ListConstructorsParams,
} from "./api.js";

export const constructorKeys = {
  all: ["constructors"] as const,
  list: (params?: ListConstructorsParams) =>
    [...constructorKeys.all, "list", params ?? {}] as const,
  detail: (id: string) => [...constructorKeys.all, "detail", id] as const,
  drivers: (id: string) => [...constructorKeys.all, "drivers", id] as const,
  statistics: (id: string) => [...constructorKeys.all, "statistics", id] as const,
  performance: (id: string) => [...constructorKeys.all, "performance", id] as const,
};

export function useConstructors(params?: ListConstructorsParams) {
  return useQuery({
    queryKey: constructorKeys.list(params),
    queryFn: () => listConstructors(params),
  });
}

export function useConstructor(constructorId: string | undefined) {
  return useQuery({
    queryKey: constructorKeys.detail(constructorId ?? ""),
    queryFn: () => getConstructor(constructorId!),
    enabled: constructorId !== undefined,
  });
}

export function useConstructorDrivers(constructorId: string | undefined) {
  return useQuery({
    queryKey: constructorKeys.drivers(constructorId ?? ""),
    queryFn: () => getConstructorDrivers(constructorId!),
    enabled: constructorId !== undefined,
  });
}

export function useConstructorStatistics(constructorId: string | undefined) {
  return useQuery({
    queryKey: constructorKeys.statistics(constructorId ?? ""),
    queryFn: () => getConstructorStatistics(constructorId!),
    enabled: constructorId !== undefined,
  });
}

export function useConstructorPerformance(constructorId: string | undefined) {
  return useQuery({
    queryKey: constructorKeys.performance(constructorId ?? ""),
    queryFn: () => getConstructorPerformance(constructorId!),
    enabled: constructorId !== undefined,
  });
}
