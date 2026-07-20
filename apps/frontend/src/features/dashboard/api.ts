import type { DashboardData, DashboardHighlights } from "@pit-wall-insight/shared-types";

import { apiGet } from "../../lib/api-client.js";

/** `GET /dashboard` (docs/08_API_SPECIFICATION.md — "Dashboard"). */
export function getDashboard(): Promise<DashboardData> {
  return apiGet<DashboardData>("/dashboard");
}

/** `GET /dashboard/highlights`. */
export function getDashboardHighlights(): Promise<DashboardHighlights> {
  return apiGet<DashboardHighlights>("/dashboard/highlights");
}
