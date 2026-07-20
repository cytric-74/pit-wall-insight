import { useQuery } from "@tanstack/react-query";

import { getTyreDegradation, type TyreDegradationParams } from "./api.js";

export const strategyKeys = {
  all: ["strategy"] as const,
  tyres: (params?: TyreDegradationParams) => [...strategyKeys.all, "tyres", params ?? {}] as const,
};

export function useTyreDegradation(params: TyreDegradationParams | undefined) {
  return useQuery({
    queryKey: strategyKeys.tyres(params),
    queryFn: () => getTyreDegradation(params),
    enabled: params !== undefined,
  });
}
