import type { ApiResponse } from "@pit-wall-insight/shared-types";

/**
 * Reusable HTTP client for the Pit Wall Insight API. Every feature's
 * `api.ts` (e.g. `features/dashboard/api.ts`) calls `apiGet` rather than
 * using `fetch` directly — this is the one place that knows the base URL,
 * how query parameters are built, how the `{success, data}`/`{success,
 * error}` envelope (`@pit-wall-insight/shared-types`) is unwrapped, and how
 * a non-2xx/`success: false` response becomes a thrown `ApiError`.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL;

export type QueryParamValue = string | number | boolean | undefined | null;

/** Thrown by `apiGet` for both transport failures and `success: false` envelopes. */
export class ApiError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function buildUrl(path: string, params?: Record<string, QueryParamValue>): string {
  const url = new URL(`${API_BASE_URL}${path}`);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

export async function apiGet<T>(
  path: string,
  params?: Record<string, QueryParamValue>,
): Promise<T> {
  const response = await fetch(buildUrl(path, params));

  let body: ApiResponse<T>;
  try {
    body = (await response.json()) as ApiResponse<T>;
  } catch {
    throw new ApiError(
      `Request to ${path} failed with status ${response.status} and no JSON body.`,
      "INVALID_RESPONSE",
      response.status,
    );
  }

  if (!body.success) {
    throw new ApiError(body.error.message, body.error.code, response.status);
  }
  return body.data;
}
