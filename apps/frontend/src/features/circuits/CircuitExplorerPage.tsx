import {
  AreaChart,
  Badge,
  Container,
  Hero,
  Select,
  Widget,
  WidgetGrid,
} from "@pit-wall-insight/ui";
import { useState } from "react";

import { getSampleCircuit, LAP_DISTANCE_MARKERS, SAMPLE_CIRCUITS } from "./data.js";
import { TrackShape } from "./TrackShape.js";

const DEFAULT_CIRCUIT_ID = SAMPLE_CIRCUITS[0]!.id;

const SECTOR_LABELS = { 1: "Sector 1", 2: "Sector 2", 3: "Sector 3" } as const;

/**
 * Circuit Explorer (docs/01_PRODUCT_REQUIREMENTS.md: interactive track
 * map, corner information, track statistics, historical winners,
 * elevation profile, sector layout). There is no dedicated "Circuit
 * Explorer Layout" section in docs/assets/04_LAYOUT_SYSTEM.md — this
 * ordering is inferred from the product requirements and
 * docs/13_ROADMAP.md's Milestone 10 feature list instead. Runs on the
 * sample data in ./data.ts — visibly badged as such — until the circuit
 * endpoints exist.
 *
 * The track map is an abstract placeholder outline (see TrackShape),
 * not a real `svg_track` trace, since no circuit geometry data exists
 * yet. Sector layout is folded into the corner list (each corner is
 * grouped under its sector) rather than given its own widget, since
 * track statistics already surface in the Hero stats.
 */
export function CircuitExplorerPage() {
  const [circuitId, setCircuitId] = useState<string>(DEFAULT_CIRCUIT_ID);
  const circuit = getSampleCircuit(circuitId) ?? SAMPLE_CIRCUITS[0]!;

  const cornersBySector = [1, 2, 3] as const;

  return (
    <>
      <Hero
        eyebrow="Circuit Explorer"
        title={circuit.name}
        description={`${circuit.city}, ${circuit.country} · ${circuit.direction}`}
        stats={[
          { label: "Length", value: circuit.lengthKm.toFixed(3), unit: "km" },
          { label: "Corners", value: String(circuit.corners) },
          { label: "DRS zones", value: String(circuit.drsZones) },
          { label: "Lap record", value: circuit.lapRecord },
        ]}
      />

      <Container className="flex flex-col gap-8 pb-(--section-gap)">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <Select
            label="Circuit"
            value={circuitId}
            onValueChange={setCircuitId}
            options={SAMPLE_CIRCUITS.map((item) => ({ value: item.id, label: item.name }))}
            className="min-w-64"
          />
          <Badge variant="warning">Sample data</Badge>
        </div>

        <WidgetGrid>
          <Widget
            title="Track map"
            description="Abstract placeholder outline — not the real circuit geometry."
            className="laptop:col-span-6"
          >
            <TrackShape shape={circuit.trackShape} />
          </Widget>

          <Widget
            title="Elevation profile"
            description="Relative elevation change around the lap."
            className="laptop:col-span-6"
          >
            <AreaChart
              categories={LAP_DISTANCE_MARKERS}
              series={[{ name: "Elevation", data: circuit.elevationProfile }]}
              xAxisLabel="Lap distance"
              yAxisLabel="m"
              valueFormatter={(value) => `${value}m`}
              ariaLabel={`${circuit.name} elevation profile, sample data`}
            />
          </Widget>

          <Widget
            title="Corner information"
            description="Notable corners, grouped by sector."
            className="laptop:col-span-6"
          >
            <div className="flex flex-col gap-4">
              {cornersBySector.map((sector) => {
                const corners = circuit.cornerInfo.filter((corner) => corner.sector === sector);
                if (corners.length === 0) return null;
                return (
                  <div key={sector} className="flex flex-col gap-2">
                    <span className="text-caption uppercase tracking-wide text-text-muted">
                      {SECTOR_LABELS[sector]}
                    </span>
                    <ol className="flex flex-col gap-2">
                      {corners.map((corner) => (
                        <li
                          key={corner.number}
                          className="flex items-center gap-3 border-b border-border-subtle pb-2 last:border-b-0 last:pb-0"
                        >
                          <span className="font-mono text-caption tabular-nums text-text-muted">
                            T{corner.number}
                          </span>
                          <span className="text-body-sm text-text-secondary">{corner.name}</span>
                        </li>
                      ))}
                    </ol>
                  </div>
                );
              })}
            </div>
          </Widget>

          <Widget
            title="Historical winners"
            description="Most recent race winners at this circuit."
            className="laptop:col-span-6"
          >
            <ol className="flex flex-col gap-2">
              {circuit.historicalWinners.map((winner) => (
                <li
                  key={winner.season}
                  className="flex items-center justify-between border-b border-border-subtle pb-2 last:border-b-0 last:pb-0"
                >
                  <span className="flex items-center gap-3">
                    <span className="font-mono text-caption tabular-nums text-text-muted">
                      {winner.season}
                    </span>
                    <span className="text-body-sm text-text-primary">{winner.driver}</span>
                  </span>
                  <span className="text-caption uppercase tracking-wide text-text-muted">
                    {winner.constructorName}
                  </span>
                </li>
              ))}
            </ol>
          </Widget>
        </WidgetGrid>
      </Container>
    </>
  );
}
