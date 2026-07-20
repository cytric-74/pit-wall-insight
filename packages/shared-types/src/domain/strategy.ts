/**
 * `/strategy/tyres` (docs/08_API_SPECIFICATION.md — "Strategy"). Mirrors
 * `apps/backend/app/schemas/strategy.py` exactly. Only tyre degradation
 * is built on the backend — `/strategy/undercut`, `/strategy/overcut`,
 * and `/strategy/simulation` all need pit-stop-timing data more complete
 * than the known `fct_pitstop` gap allows (see
 * `apps/backend/app/models/gold/pitstop.py`), so there are no types for
 * them here.
 */

export interface TyreDegradationPoint {
  compound: string;
  tyreLife: number;
  averageLapTime: number;
  sampleCount: number;
}

export interface TyreDegradation {
  points: TyreDegradationPoint[];
}
