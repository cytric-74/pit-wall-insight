import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  CONSTRUCTOR_THEMES,
  getConstructorTheme,
  isConstructorId,
  type ConstructorId,
  type ConstructorTheme,
} from "./constructors.js";

const DEFAULT_STORAGE_KEY = "pit-wall-insight:constructor";
const THEME_ATTRIBUTE = "data-constructor";

interface ConstructorThemeContextValue {
  /** Selected constructor id, or `null` for the default (unbranded) theme. */
  constructorId: ConstructorId | null;
  /** Resolved theme data for the current selection, if any. */
  constructor: ConstructorTheme | undefined;
  /** Every constructor theme available to choose from. */
  constructors: readonly ConstructorTheme[];
  setConstructor: (id: ConstructorId | null) => void;
}

const ConstructorThemeContext = createContext<ConstructorThemeContextValue | null>(null);

export interface ThemeProviderProps {
  children: ReactNode;
  /** Constructor selected before the user (or persisted storage) picks one. */
  defaultConstructor?: ConstructorId | null;
  /** localStorage key used to persist the selection across sessions. */
  storageKey?: string;
}

/**
 * Applies the active constructor as `data-constructor` on `<html>`.
 *
 * This provider owns *selection state* only — every actual color value
 * lives in CSS (`@pit-wall-insight/config/tailwind/constructor-themes.css`),
 * keyed off the same attribute. Nothing here injects inline styles or
 * touches typography/layout/motion, per docs/assets/12_THEME_ENGINE.md:
 * "Themes personalize the experience. They never redesign it."
 */
export function ThemeProvider({
  children,
  defaultConstructor = null,
  storageKey = DEFAULT_STORAGE_KEY,
}: ThemeProviderProps): ReactNode {
  const [constructorId, setConstructorId] = useState<ConstructorId | null>(() => {
    if (typeof window === "undefined") return defaultConstructor;
    const stored = window.localStorage.getItem(storageKey);
    return isConstructorId(stored) ? stored : defaultConstructor;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (constructorId) {
      root.setAttribute(THEME_ATTRIBUTE, constructorId);
    } else {
      root.removeAttribute(THEME_ATTRIBUTE);
    }
  }, [constructorId]);

  useEffect(() => {
    if (constructorId) {
      window.localStorage.setItem(storageKey, constructorId);
    } else {
      window.localStorage.removeItem(storageKey);
    }
  }, [constructorId, storageKey]);

  const setConstructor = useCallback((id: ConstructorId | null) => {
    setConstructorId(id);
  }, []);

  const value = useMemo<ConstructorThemeContextValue>(
    () => ({
      constructorId,
      constructor: getConstructorTheme(constructorId),
      constructors: CONSTRUCTOR_THEMES,
      setConstructor,
    }),
    [constructorId, setConstructor],
  );

  return (
    <ConstructorThemeContext.Provider value={value}>{children}</ConstructorThemeContext.Provider>
  );
}

export function useConstructorTheme(): ConstructorThemeContextValue {
  const context = useContext(ConstructorThemeContext);
  if (!context) {
    throw new Error("useConstructorTheme must be used within a <ThemeProvider>.");
  }
  return context;
}
