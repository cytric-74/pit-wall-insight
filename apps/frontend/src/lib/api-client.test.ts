import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { apiGet, apiGetCollection, ApiError } from "./api-client.js";

function jsonResponse(body: unknown, status = 200): Response {
  return { status, json: () => Promise.resolve(body) } as unknown as Response;
}

function invalidJsonResponse(status = 500): Response {
  return { status, json: () => Promise.reject(new Error("not json")) } as unknown as Response;
}

describe("apiGet", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("unwraps the {success, data} envelope", async () => {
    vi.mocked(fetch).mockResolvedValue(jsonResponse({ success: true, data: { id: "1" } }));

    const result = await apiGet<{ id: string }>("/drivers/1");

    expect(result).toEqual({ id: "1" });
  });

  it("throws ApiError with the envelope's code/message on a success: false response", async () => {
    vi.mocked(fetch).mockResolvedValue(
      jsonResponse(
        { success: false, error: { code: "NOT_FOUND", message: "Driver not found." } },
        404,
      ),
    );

    await expect(apiGet("/drivers/unknown")).rejects.toMatchObject({
      name: "ApiError",
      code: "NOT_FOUND",
      message: "Driver not found.",
      status: 404,
    });
  });

  it("throws ApiError for a response with no parseable JSON body", async () => {
    vi.mocked(fetch).mockResolvedValue(invalidJsonResponse(500));

    await expect(apiGet("/drivers/1")).rejects.toMatchObject({
      name: "ApiError",
      code: "INVALID_RESPONSE",
      status: 500,
    });
  });

  it("omits undefined/null query parameters from the request URL", async () => {
    const fetchMock = vi.mocked(fetch);
    fetchMock.mockResolvedValue(jsonResponse({ success: true, data: [] }));

    await apiGet("/drivers", { season: 2024, constructorId: undefined, active: null });

    const requestedUrl = new URL(fetchMock.mock.calls[0]![0] as string);
    expect(requestedUrl.searchParams.get("season")).toBe("2024");
    expect(requestedUrl.searchParams.has("constructorId")).toBe(false);
    expect(requestedUrl.searchParams.has("active")).toBe(false);
  });
});

describe("apiGetCollection", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("unwraps the {success, data, pagination} envelope", async () => {
    const pagination = { page: 1, limit: 25, total: 2, totalPages: 1 };
    vi.mocked(fetch).mockResolvedValue(
      jsonResponse({ success: true, data: [{ id: "1" }], pagination }),
    );

    const result = await apiGetCollection<{ id: string }>("/drivers");

    expect(result).toEqual({ data: [{ id: "1" }], pagination });
  });

  it("throws ApiError on a success: false response", async () => {
    vi.mocked(fetch).mockResolvedValue(
      jsonResponse(
        { success: false, error: { code: "VALIDATION_ERROR", message: "Bad query." } },
        422,
      ),
    );

    await expect(apiGetCollection("/drivers")).rejects.toBeInstanceOf(ApiError);
  });
});
