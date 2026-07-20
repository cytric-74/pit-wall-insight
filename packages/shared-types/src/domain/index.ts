/**
 * Domain entity contracts (Driver, Constructor, Race, Session, Lap,
 * Telemetry, PitStop, Circuit, Season, ...), one module per resource,
 * added as each is wired up to the real backend API
 * (apps/backend/app/api/v1/). Mirrors the backend's Pydantic response
 * schemas rather than the raw database schema (docs/07_DATABASE_SCHEMA.md)
 * — these are API contracts, not ORM mirrors.
 */

export * from "./dashboard.js";
export * from "./driver.js";
export * from "./race.js";
export * from "./session.js";
