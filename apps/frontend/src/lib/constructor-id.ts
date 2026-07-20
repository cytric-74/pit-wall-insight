import { CONSTRUCTOR_THEMES } from "@pit-wall-insight/ui";

/**
 * The backend returns free-text constructor names (`dim_constructor.team_name`
 * — see apps/backend/app/models/gold/constructor.py), not the design
 * system's fixed theme slugs (`ConstructorId`, packages/ui/src/theme/constructors.ts).
 * Most 2024-grid names match a theme's `name` field directly ("Ferrari",
 * "Red Bull", ...); a few don't, because the backend's source data uses a
 * team's full sponsor-laden name where the theme registry uses its short
 * one. This reconciles the two. Falls back to `undefined` for an
 * unrecognized name, exactly like `getConstructorTheme` already does for an
 * unknown id — never fabricates a theme.
 */

const ALIASES: Readonly<Record<string, string>> = {
  "haas f1 team": "haas",
  "alpine f1 team": "alpine",
  sauber: "kick-sauber",
  "rb f1 team": "racing-bulls",
};

const THEME_ID_BY_NAME = new Map(
  CONSTRUCTOR_THEMES.map((theme) => [theme.name.toLowerCase(), theme.id]),
);

export function resolveConstructorId(teamName: string | null | undefined): string | undefined {
  if (!teamName) return undefined;
  const key = teamName.toLowerCase();
  return THEME_ID_BY_NAME.get(key) ?? ALIASES[key];
}
