import { useReducedMotion as useFramerReducedMotion } from "framer-motion";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

const DEFAULT_STORAGE_KEY = "pit-wall-insight:preferences";
const MOTION_ATTRIBUTE = "data-motion";
const CONTRAST_ATTRIBUTE = "data-contrast";

export type SpeedUnit = "kph" | "mph";
export type TemperatureUnit = "celsius" | "fahrenheit";
/** "system" defers to the OS `prefers-reduced-motion` signal; "reduced" forces it on regardless. */
export type MotionPreference = "system" | "reduced";

export interface Preferences {
  speedUnit: SpeedUnit;
  temperatureUnit: TemperatureUnit;
  motion: MotionPreference;
  highContrast: boolean;
}

const DEFAULT_PREFERENCES: Preferences = {
  speedUnit: "kph",
  temperatureUnit: "celsius",
  motion: "system",
  highContrast: false,
};

function readStoredPreferences(storageKey: string): Preferences {
  if (typeof window === "undefined") return DEFAULT_PREFERENCES;
  try {
    const raw = window.localStorage.getItem(storageKey);
    if (!raw) return DEFAULT_PREFERENCES;
    const parsed: unknown = JSON.parse(raw);
    if (typeof parsed !== "object" || parsed === null) return DEFAULT_PREFERENCES;
    return { ...DEFAULT_PREFERENCES, ...(parsed as Partial<Preferences>) };
  } catch {
    return DEFAULT_PREFERENCES;
  }
}

interface PreferencesContextValue {
  preferences: Preferences;
  setSpeedUnit: (unit: SpeedUnit) => void;
  setTemperatureUnit: (unit: TemperatureUnit) => void;
  setMotion: (motion: MotionPreference) => void;
  setHighContrast: (enabled: boolean) => void;
}

const PreferencesContext = createContext<PreferencesContextValue | null>(null);

export interface PreferencesProviderProps {
  children: ReactNode;
  /** localStorage key used to persist preferences across sessions. */
  storageKey?: string;
}

/**
 * Owns app-wide preferences that aren't part of constructor theming
 * (telemetry units, motion, contrast) — a separate axis from
 * `ThemeProvider`, which only ever touches constructor color tokens
 * (docs/assets/12_THEME_ENGINE.md: "themes personalize, they never
 * redesign"). Persists as a single JSON blob, same pattern as
 * `ThemeProvider`'s localStorage handling.
 *
 * Motion and contrast are applied via `data-motion`/`data-contrast`
 * attributes on `<html>`, read by packages/config/tailwind/tokens.css —
 * the same "attribute drives CSS custom properties" approach the
 * constructor theme uses, so no component needs its own reduced-motion
 * or contrast branching logic for anything already built on duration/
 * color tokens.
 */
export function PreferencesProvider({
  children,
  storageKey = DEFAULT_STORAGE_KEY,
}: PreferencesProviderProps): ReactNode {
  const [preferences, setPreferences] = useState<Preferences>(() =>
    readStoredPreferences(storageKey),
  );

  useEffect(() => {
    const root = document.documentElement;
    if (preferences.motion === "reduced") {
      root.setAttribute(MOTION_ATTRIBUTE, "reduced");
    } else {
      root.removeAttribute(MOTION_ATTRIBUTE);
    }
  }, [preferences.motion]);

  useEffect(() => {
    const root = document.documentElement;
    if (preferences.highContrast) {
      root.setAttribute(CONTRAST_ATTRIBUTE, "high");
    } else {
      root.removeAttribute(CONTRAST_ATTRIBUTE);
    }
  }, [preferences.highContrast]);

  useEffect(() => {
    window.localStorage.setItem(storageKey, JSON.stringify(preferences));
  }, [preferences, storageKey]);

  const setSpeedUnit = useCallback((speedUnit: SpeedUnit) => {
    setPreferences((current) => ({ ...current, speedUnit }));
  }, []);

  const setTemperatureUnit = useCallback((temperatureUnit: TemperatureUnit) => {
    setPreferences((current) => ({ ...current, temperatureUnit }));
  }, []);

  const setMotion = useCallback((motion: MotionPreference) => {
    setPreferences((current) => ({ ...current, motion }));
  }, []);

  const setHighContrast = useCallback((highContrast: boolean) => {
    setPreferences((current) => ({ ...current, highContrast }));
  }, []);

  const value = useMemo<PreferencesContextValue>(
    () => ({ preferences, setSpeedUnit, setTemperatureUnit, setMotion, setHighContrast }),
    [preferences, setSpeedUnit, setTemperatureUnit, setMotion, setHighContrast],
  );

  return <PreferencesContext.Provider value={value}>{children}</PreferencesContext.Provider>;
}

export function usePreferences(): PreferencesContextValue {
  const context = useContext(PreferencesContext);
  if (!context) {
    throw new Error("usePreferences must be used within a <PreferencesProvider>.");
  }
  return context;
}

/**
 * Combines the OS-level `prefers-reduced-motion` signal with the
 * in-app override, so JS-driven animation (anything not expressed as a
 * CSS duration token) can respect both with a single check.
 */
export function usePrefersReducedMotion(): boolean {
  const systemPrefersReduced = useFramerReducedMotion();
  const { preferences } = usePreferences();
  return preferences.motion === "reduced" || Boolean(systemPrefersReduced);
}
