/**
 * Shared API envelope contracts.
 *
 * Mirrors the response shape the backend already produces
 * (apps/backend/app/schemas/common.py, docs/08_API_SPECIFICATION.md) so the
 * frontend can type API responses without redefining the contract.
 */

export interface ApiMeta {
  requestId?: string;
  executionTime?: string;
}

export interface ApiSuccessResponse<T> {
  success: true;
  data: T;
  meta?: ApiMeta;
}

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

export interface ApiCollectionResponse<T> {
  success: true;
  data: T[];
  pagination: PaginationMeta;
}

export interface ApiErrorDetail {
  code: string;
  message: string;
  details?: unknown;
}

export interface ApiErrorResponse {
  success: false;
  error: ApiErrorDetail;
  requestId?: string;
}

export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;
