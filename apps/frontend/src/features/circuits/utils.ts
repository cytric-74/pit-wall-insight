import type { TrackShapeKind } from "./TrackShape.js";

const SHAPES: readonly TrackShapeKind[] = ["loop", "chicane", "oval"];

/** Assigns one of the three abstract track outlines to a real circuit id —
 * stable per circuit (same id always draws the same shape), but arbitrary;
 * purely for visual variety since no real track geometry exists (see
 * `TrackShape.tsx`). */
export function pickTrackShape(circuitId: string): TrackShapeKind {
  let hash = 0;
  for (let index = 0; index < circuitId.length; index += 1) {
    hash = (hash * 31 + circuitId.charCodeAt(index)) % SHAPES.length;
  }
  return SHAPES[Math.abs(hash) % SHAPES.length]!;
}
