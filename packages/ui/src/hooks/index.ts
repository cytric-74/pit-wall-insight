/**
 * Shared hooks: useTheme, useBreakpoint, useConstructorTheme,
 * useIntersection, useAnimation, useTooltip, useResize, useChart,
 * useKeyboard, useFilters (docs/09_COMPONENT_LIBRARY.md, "Shared Hooks").
 *
 * The docs describe these hooks but don't assign them a folder in the
 * component directory diagram — `hooks/` is the natural home and is added
 * here for that reason.
 *
 * `useConstructorTheme` is already implemented, but lives in and is
 * exported from `../theme/` (alongside the provider and constructor data
 * it reads) rather than being re-exported here too, to avoid two barrels
 * exporting the same name. The rest of these hooks are not implemented
 * yet.
 */

export {};
