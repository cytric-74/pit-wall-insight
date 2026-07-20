import type { TyreDegradation } from "@pit-wall-insight/shared-types";

import { apiGet, type QueryParamValue } from "../../lib/api-client.js";

export interface TyreDegradationParams {
  season?: number;
  driver?: string;
  race?: number;
  session?: string;
  [key: string]: QueryParamValue;
}

/** `GET /strategy/tyres` (docs/08_API_SPECIFICATION.md — "Strategy"). */
export function getTyreDegradation(params?: TyreDegradationParams): Promise<TyreDegradation> {
  return apiGet<TyreDegradation>("/strategy/tyres", params);
}
