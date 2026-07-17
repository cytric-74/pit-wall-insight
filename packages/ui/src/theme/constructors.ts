/**
 * Constructor theme registry (docs/03_DESIGN_SYSTEM.md — Team Color
 * Tokens; docs/assets/12_THEME_ENGINE.md — Constructor Identity).
 *
 * Each entry supplies the CSS variable overrides applied on
 * `[data-constructor="<id>"]` in constructor-themes.css — nothing else
 * about the interface changes when a constructor is selected
 * (docs/assets/12_THEME_ENGINE.md: "Structure remains permanent.
 * Personality changes.").
 */

export interface ConstructorTheme {
  id: string;
  name: string;
  primary: string;
  secondary: string;
}

export const CONSTRUCTOR_THEMES: readonly ConstructorTheme[] = [
  { id: "ferrari", name: "Ferrari", primary: "#DC0000", secondary: "#FF5A5A" },
  { id: "mercedes", name: "Mercedes", primary: "#00D2BE", secondary: "#71FFF2" },
  { id: "mclaren", name: "McLaren", primary: "#FF8700", secondary: "#FFBE73" },
  { id: "red-bull", name: "Red Bull", primary: "#1E5BC6", secondary: "#5D93F5" },
  { id: "aston-martin", name: "Aston Martin", primary: "#006F62", secondary: "#4EC5B7" },
  { id: "williams", name: "Williams", primary: "#005AFF", secondary: "#6EAEFF" },
  { id: "alpine", name: "Alpine", primary: "#FF87BC", secondary: "#FFD0E4" },
  { id: "racing-bulls", name: "Visa Cash App RB", primary: "#6692FF", secondary: "#A9C3FF" },
  { id: "haas", name: "Haas", primary: "#B6BABD", secondary: "#ECECEC" },
  { id: "kick-sauber", name: "Kick Sauber", primary: "#52E252", secondary: "#A9FFA9" },
] as const;

export type ConstructorId = (typeof CONSTRUCTOR_THEMES)[number]["id"];

const CONSTRUCTOR_THEME_BY_ID = new Map(
  CONSTRUCTOR_THEMES.map((constructor) => [constructor.id, constructor]),
);

export function getConstructorTheme(id: string | null | undefined): ConstructorTheme | undefined {
  if (!id) return undefined;
  return CONSTRUCTOR_THEME_BY_ID.get(id);
}

export function isConstructorId(id: string | null | undefined): id is ConstructorId {
  return id != null && CONSTRUCTOR_THEME_BY_ID.has(id);
}
