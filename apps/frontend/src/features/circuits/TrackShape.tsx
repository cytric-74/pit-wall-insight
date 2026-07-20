/**
 * Abstract placeholder track outlines — not geographically accurate to
 * the real circuits (docs/assets/10_ICONOGRAPHY.md: "Circuit Icons: use
 * simplified track representations, avoid decorative circuit graphics").
 * This stays a placeholder even with the real backend wired up: no
 * `svg_track` geometry is collected anywhere in this pipeline
 * (apps/backend/app/models/gold/circuit.py), so there is no real trace to
 * draw instead — see `pickTrackShape` in `./utils.ts` for how a circuit is
 * assigned one of these three purely for visual variety.
 */
export type TrackShapeKind = "loop" | "chicane" | "oval";

const TRACK_PATHS: Record<TrackShapeKind, string> = {
  loop: "M20 90 L20 40 Q20 20 40 20 L120 20 Q140 20 140 40 L140 60 Q140 80 160 80 L220 80 Q240 80 240 100 L240 140 Q240 160 220 160 L60 160 Q20 160 20 130 Z",
  chicane:
    "M20 100 L20 50 Q20 20 50 20 L100 20 L110 40 L130 20 L180 20 Q220 20 220 60 L220 90 L190 90 L190 110 L220 110 Q240 110 240 140 Q240 160 220 160 L60 160 Q20 160 20 130 Z",
  oval: "M40 30 L200 30 Q240 30 240 90 Q240 150 200 150 L40 150 Q20 150 20 90 Q20 30 40 30 Z",
};

export function TrackShape({ shape }: { shape: TrackShapeKind }) {
  return (
    <svg
      viewBox="0 0 260 180"
      className="h-auto w-full text-constructor-primary"
      fill="none"
      role="img"
      aria-label="Abstract circuit track outline"
    >
      <rect x="0.5" y="0.5" width="259" height="179" rx="16" className="stroke-border-default" />
      <path d={TRACK_PATHS[shape]} stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
