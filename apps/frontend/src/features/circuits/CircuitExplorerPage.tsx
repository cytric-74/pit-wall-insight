import { Container, Hero, Section, Select, Stat } from "@pit-wall-insight/ui";
import { useState } from "react";

import { EmptyState } from "../../lib/empty-state.js";
import { QueryError } from "../../lib/query-error.js";
import { useCircuit, useCircuitHistory, useCircuitRecords, useCircuits } from "./queries.js";
import { TrackShape } from "./TrackShape.js";
import { pickTrackShape } from "./utils.js";

/**
 * Circuit Explorer (docs/01_PRODUCT_REQUIREMENTS.md: interactive track
 * map, corner information, track statistics, historical winners,
 * elevation profile, sector layout). Backed by `/api/v1/circuits/*`
 * (docs/08_API_SPECIFICATION.md — "Circuits").
 *
 * Editorial rebuild: the track outline is no longer one of four
 * equal-weight widgets — it's the page's organizing graphic, large,
 * paired directly with the lap-record numbers beside it (the redesign
 * brief's reference-inspired "big number next to a big diagram" layout),
 * with a thin divider standing in for the reference's diagonal rule.
 * Historical winners is the one dense secondary list. "Elevation profile"
 * and "Corner information" have no data source at all in this pipeline —
 * rather than two more permanent fake-loading skeletons, that's one
 * honest sentence instead.
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
        title={
          circuitQuery.isError ? "Couldn't load circuit" : (circuit?.name ?? "Loading circuit…")
        }
        description={[circuit?.city, circuit?.country]
          .filter((part): part is string => Boolean(part))
          .join(", ")}
      />

      <Container className="flex flex-wrap items-end justify-between gap-4 py-8">
        <Select
          label="Circuit"
          {...(circuitId !== undefined && { value: circuitId })}
          onValueChange={setSelectedId}
          options={circuits.map((item) => ({ value: item.id, label: item.name }))}
          className="min-w-64"
        />
      </Container>

      <Section
        title="Track"
        description="Abstract placeholder outline — not the real circuit geometry."
      >
        {circuitQuery.isError ? (
          <QueryError />
        ) : (
          <div className="grid grid-cols-1 items-center gap-12 laptop:grid-cols-[minmax(0,1fr)_280px]">
            {circuitId ? <TrackShape shape={pickTrackShape(circuitId)} /> : null}
            <div className="flex flex-col gap-8 border-t border-border-subtle pt-8 laptop:border-l laptop:border-t-0 laptop:pl-12 laptop:pt-0">
              <Stat
                label="Fastest lap"
                value={record?.lapTime != null ? record.lapTime.toFixed(3) : "—"}
                unit="s"
                variant="hero"
                {...(record?.driver != null && { caption: record.driver })}
              />
              <Stat
                label="Races hosted"
                value={historyQuery.isPending || historyQuery.isError ? "—" : history.length}
              />
            </div>
          </div>
        )}

        <p className="mt-10 font-mono text-caption uppercase tracking-wide text-text-muted">
          Elevation profile and corner-by-corner data aren't available for this circuit yet.
        </p>
      </Section>

      <Section title="Historical winners" description="Most recent race winners at this circuit.">
        {historyQuery.isError ? (
          <QueryError />
        ) : history.length === 0 ? (
          <EmptyState message={historyQuery.isPending ? "Syncing telemetry…" : "No races found"} />
        ) : (
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
                <span className="font-mono text-caption uppercase tracking-wide text-text-muted">
                  {entry.raceName ?? "—"}
                </span>
              </li>
            ))}
          </ol>
        )}
      </Section>
    </>
  );
}
