/**
 * The widget-level "this list has nothing in it yet" state. Every
 * `.map()` over a possibly-empty array (standings, historical winners,
 * race events, final classification, pit windows) rendered nothing at all
 * when empty — indistinguishable from "still loading" or "silently
 * broken," and not hypothetical: several real endpoints legitimately
 * return empty arrays today (e.g. pit stops, per the documented
 * `fct_pitstop` gap) (Phase 7 audit, High). Reuses the same
 * `text-caption text-text-muted` treatment already used for the "No data
 * yet" branch of `MissionControlPage`'s `KpiWidget`.
 */
export function EmptyState({ message = "No data yet" }: { message?: string }) {
  return <p className="text-caption text-text-muted">{message}</p>;
}
