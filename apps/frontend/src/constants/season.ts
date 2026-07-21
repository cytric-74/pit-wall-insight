/**
 * SAMPLE DATA — placeholder season calendar, currently only consumed by
 * `features/season/` (Constructors and Drivers have since migrated off
 * sample data). Kept here rather than inside `features/season/` because
 * features never import from each other directly (docs/04_FRONTEND_ARCHITECTURE.md),
 * so any shared sample fixture — even a single-consumer one today — lives
 * in this top-level constants module, not inside one feature's own folder.
 */
export const SAMPLE_ROUNDS: readonly string[] = [
  "BHR",
  "SAU",
  "AUS",
  "JPN",
  "CHN",
  "MIA",
  "EMI",
  "MON",
];
