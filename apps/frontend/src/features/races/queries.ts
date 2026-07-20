import { useQuery } from "@tanstack/react-query";

import {
  getCurrentSeasonRaces,
  getRace,
  getRacePitstops,
  getRacePositions,
  getRaceStrategy,
  getRaceWeather,
  listRaces,
  type ListRacesParams,
} from "./api.js";

export const raceKeys = {
  all: ["races"] as const,
  list: (params?: ListRacesParams) => [...raceKeys.all, "list", params ?? {}] as const,
  detail: (id: string) => [...raceKeys.all, "detail", id] as const,
  positions: (id: string) => [...raceKeys.all, "positions", id] as const,
  pitstops: (id: string) => [...raceKeys.all, "pitstops", id] as const,
  weather: (id: string) => [...raceKeys.all, "weather", id] as const,
  strategy: (id: string) => [...raceKeys.all, "strategy", id] as const,
};

export function useRaces(params?: ListRacesParams) {
  return useQuery({
    queryKey: raceKeys.list(params),
    queryFn: () => listRaces(params),
  });
}

export function useRace(raceId: string | undefined) {
  return useQuery({
    queryKey: raceKeys.detail(raceId ?? ""),
    queryFn: () => getRace(raceId!),
    enabled: raceId !== undefined,
  });
}

export function useRacePositions(raceId: string | undefined) {
  return useQuery({
    queryKey: raceKeys.positions(raceId ?? ""),
    queryFn: () => getRacePositions(raceId!),
    enabled: raceId !== undefined,
  });
}

export function useRacePitstops(raceId: string | undefined) {
  return useQuery({
    queryKey: raceKeys.pitstops(raceId ?? ""),
    queryFn: () => getRacePitstops(raceId!),
    enabled: raceId !== undefined,
  });
}

export function useRaceWeather(raceId: string | undefined) {
  return useQuery({
    queryKey: raceKeys.weather(raceId ?? ""),
    queryFn: () => getRaceWeather(raceId!),
    enabled: raceId !== undefined,
  });
}

export function useRaceStrategy(raceId: string | undefined) {
  return useQuery({
    queryKey: raceKeys.strategy(raceId ?? ""),
    queryFn: () => getRaceStrategy(raceId!),
    enabled: raceId !== undefined,
  });
}

export function useCurrentSeasonRaces() {
  return useQuery({
    queryKey: ["races", "current-season"] as const,
    queryFn: getCurrentSeasonRaces,
  });
}
