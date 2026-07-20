import { useQuery } from "@tanstack/react-query";

import {
  getCircuit,
  getCircuitHistory,
  getCircuitRecords,
  listCircuits,
  type ListCircuitsParams,
} from "./api.js";

export const circuitKeys = {
  all: ["circuits"] as const,
  list: (params?: ListCircuitsParams) => [...circuitKeys.all, "list", params ?? {}] as const,
  detail: (id: string) => [...circuitKeys.all, "detail", id] as const,
  history: (id: string) => [...circuitKeys.all, "history", id] as const,
  records: (id: string) => [...circuitKeys.all, "records", id] as const,
};

export function useCircuits(params?: ListCircuitsParams) {
  return useQuery({
    queryKey: circuitKeys.list(params),
    queryFn: () => listCircuits(params),
  });
}

export function useCircuit(circuitId: string | undefined) {
  return useQuery({
    queryKey: circuitKeys.detail(circuitId ?? ""),
    queryFn: () => getCircuit(circuitId!),
    enabled: circuitId !== undefined,
  });
}

export function useCircuitHistory(circuitId: string | undefined) {
  return useQuery({
    queryKey: circuitKeys.history(circuitId ?? ""),
    queryFn: () => getCircuitHistory(circuitId!),
    enabled: circuitId !== undefined,
  });
}

export function useCircuitRecords(circuitId: string | undefined) {
  return useQuery({
    queryKey: circuitKeys.records(circuitId ?? ""),
    queryFn: () => getCircuitRecords(circuitId!),
    enabled: circuitId !== undefined,
  });
}
