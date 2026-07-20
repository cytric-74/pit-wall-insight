import type {
  DriverStrategy,
  PitstopEntry,
  PositionEntry,
  RaceListItem,
  RaceSummary,
  RaceWeather,
  SessionResultEntry,
} from "@pit-wall-insight/shared-types";

import { apiGet, apiGetCollection, type QueryParamValue } from "../../lib/api-client.js";

export interface ListRacesParams {
  season?: number;
  country?: string;
  page?: number;
  limit?: number;
  [key: string]: QueryParamValue;
}

/** `GET /races` (docs/08_API_SPECIFICATION.md — "Races"). */
export function listRaces(params?: ListRacesParams): Promise<{ data: RaceListItem[] }> {
  return apiGetCollection<RaceListItem>("/races", params);
}

/** `GET /races/{id}`. */
export function getRace(raceId: string): Promise<RaceSummary> {
  return apiGet<RaceSummary>(`/races/${raceId}`);
}

/** `GET /races/{id}/positions` — every driver's position after each lap. */
export function getRacePositions(raceId: string): Promise<PositionEntry[]> {
  return apiGet<PositionEntry[]>(`/races/${raceId}/positions`);
}

/** `GET /races/{id}/pitstops`. */
export function getRacePitstops(raceId: string): Promise<PitstopEntry[]> {
  return apiGet<PitstopEntry[]>(`/races/${raceId}/pitstops`);
}

/** `GET /races/{id}/weather` — a single per-session snapshot, not a time series. */
export function getRaceWeather(raceId: string): Promise<RaceWeather> {
  return apiGet<RaceWeather>(`/races/${raceId}/weather`);
}

/** `GET /races/{id}/strategy` — tyre stints per driver. */
export function getRaceStrategy(raceId: string): Promise<DriverStrategy[]> {
  return apiGet<DriverStrategy[]>(`/races/${raceId}/strategy`);
}

/**
 * The current season's races, in round order — built from `GET /races`
 * (no dedicated "current season" endpoint exists) by taking the most
 * recent season present in the (season desc, round desc)-ordered list.
 * Shared by any feature that needs a season timeline reconstructed from
 * individual race results (Drivers' per-round position history,
 * Constructors' season performance/driver comparison charts).
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
