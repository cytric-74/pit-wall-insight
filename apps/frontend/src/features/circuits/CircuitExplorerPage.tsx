import { Container, Hero, Select, Widget, WidgetGrid } from "@pit-wall-insight/ui";
import { useState } from "react";

import { useCircuit, useCircuitHistory, useCircuitRecords, useCircuits } from "./queries.js";
import { TrackShape } from "./TrackShape.js";
import { pickTrackShape } from "./utils.js";

/**
 * Circuit Explorer (docs/01_PRODUCT_REQUIREMENTS.md: interactive track
 * map, corner information, track statistics, historical winners,
 * elevation profile, sector layout). There is no dedicated "Circuit
 * Explorer Layout" section in docs/assets/04_LAYOUT_SYSTEM.md — this
 * ordering is inferred from the product requirements and
 * docs/13_ROADMAP.md's Milestone 10 feature list instead. Backed by
 * `/api/v1/circuits/*` (docs/08_API_SPECIFICATION.md — "Circuits").
 *
 * "Track map" stays an abstract placeholder outline (see TrackShape) —
 * that was never sample data waiting to be replaced, it's a permanent
 * design choice, since no real circuit geometry (`svg_track`) is
 * collected anywhere in this pipeline. "Elevation profile" and "Corner
 * information" have no data source at all (nothing in `dim_circuit`
 * covers either) and stay permanent `loading` placeholders, the same
 * pattern used for "Telemetry" on the Driver Dossier and "Strategy
 * tendencies" on Constructor Intelligence.
 */
export function CircuitExplorerPage() {
  const [selectedId, setSelectedId] = useState<string | undefined>(undefined);

  const circuitsQuery = useCircuits({ limit: 100 });
  const circuits = circuitsQuery.data?.data ?? [];
  const circuitId = selectedId ?? circuits[0]?.id;

  const circuitQuery = useCircuit(circuitId);
  const circuit = circuitQuery.data;
  const historyQuery = useCircuitHistory(circuitId);
  const history = historyQuery.data ?? [];
  const recordsQuery = useCircuitRecords(circuitId);
  const record = recordsQuery.data;

  return (
    <>
      <Hero
        eyebrow="Circuit Explorer"
        title={circuit?.name ?? "Loading circuit…"}
        description={[circuit?.city, circuit?.country]
          .filter((part): part is string => Boolean(part))
          .join(", ")}
        stats={[
          { label: "Races hosted", value: historyQuery.isPending ? "—" : String(history.length) },
          {
            label: "Fastest lap",
            value: record?.lapTime != null ? `${record.lapTime.toFixed(3)}s` : "—",
          },
          { label: "Fastest lap driver", value: record?.driver ?? "—" },
        ]}
      />

      <Container className="flex flex-col gap-8 pb-(--section-gap)">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <Select
            label="Circuit"
            {...(circuitId !== undefined && { value: circuitId })}
            onValueChange={setSelectedId}
            options={circuits.map((item) => ({ value: item.id, label: item.name }))}
            className="min-w-64"
          />
        </div>

        <WidgetGrid>
          <Widget
            title="Track map"
            description="Abstract placeholder outline — not the real circuit geometry."
            className="laptop:col-span-6"
          >
            {circuitId ? <TrackShape shape={pickTrackShape(circuitId)} /> : null}
          </Widget>

          <Widget
            title="Elevation profile"
            description="Relative elevation change around the lap."
            loading
            className="laptop:col-span-6"
          />

          <Widget
            title="Corner information"
            description="Notable corners, grouped by sector."
            loading
            className="laptop:col-span-6"
          />

          <Widget
            title="Historical winners"
            description="Most recent race winners at this circuit."
            loading={historyQuery.isPending}
            className="laptop:col-span-6"
          >
            <ol className="flex flex-col gap-2">
              {history.map((entry) => (
                <li
                  key={`${entry.season}-${entry.round}`}
                  className="flex items-center justify-between border-b border-border-subtle pb-2 last:border-b-0 last:pb-0"
                >
                  <span className="flex items-center gap-3">
                    <span className="font-mono text-caption tabular-nums text-text-muted">
                      {entry.season}
                    </span>
                    <span className="text-body-sm text-text-primary">{entry.winner ?? "—"}</span>
                  </span>
                  <span className="text-caption uppercase tracking-wide text-text-muted">
                    {entry.raceName ?? "—"}
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
