/**
 * App-level theme integration point (docs/04_FRONTEND_ARCHITECTURE.md lists
 * `src/themes/` in the project structure). Also re-exports
 * `PreferencesProvider` — a separate axis of persisted app state (units,
 * motion, contrast) that lives next to the constructor theme provider in
 * `@pit-wall-insight/ui` for the same reason.
 *
 * The providers, hooks, and constructor registry are implemented in
 * `@pit-wall-insight/ui` (a shared, reusable piece — see that package's
 * `src/theme/`) rather than here, since `apps/frontend` is the one thing
 * they're consumed *by*, not the layer that should own them. This module
 * just re-exports them as the app's integration seam, so app code always
 * imports theming from `@/themes` rather than reaching into `ui` directly.
 */
export {
  ThemeProvider,
  useConstructorTheme,
  CONSTRUCTOR_THEMES,
  getConstructorTheme,
  isConstructorId,
  type ConstructorId,
  type ConstructorTheme,
  type ThemeProviderProps,
  PreferencesProvider,
  usePreferences,
  usePrefersReducedMotion,
  type Preferences,
  type PreferencesProviderProps,
  type SpeedUnit,
  type TemperatureUnit,
  type MotionPreference,
} from "@pit-wall-insight/ui";
