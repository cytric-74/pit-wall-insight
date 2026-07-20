import { useQuery } from "@tanstack/react-query";

import { getDashboard, getDashboardHighlights } from "./api.js";

export const dashboardKeys = {
  all: ["dashboard"] as const,
  overview: () => [...dashboardKeys.all, "overview"] as const,
  highlights: () => [...dashboardKeys.all, "highlights"] as const,
};

export function useDashboard() {
  return useQuery({
    queryKey: dashboardKeys.overview(),
    queryFn: getDashboard,
  });
}

export function useDashboardHighlights() {
  return useQuery({
    queryKey: dashboardKeys.highlights(),
    queryFn: getDashboardHighlights,
  });
}
