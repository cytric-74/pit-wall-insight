import {
  Badge,
  BarChart,
  Container,
  Hero,
  LineChart,
  Select,
  Widget,
  WidgetGrid,
} from "@pit-wall-insight/ui";
import { useState } from "react";

import { useRacePitstops, useRaces, useRaceStrategy } from "../races/queries.js";
import { useTyreDegradation } from "./queries.js";
import {
  buildDegradationSeries,
  computeCompoundEffectiveness,
  resolveCompoundBadgeVariant,
} from "./utils.js";

const RACE_SESSION_TYPE = "R";

/**
 * Strategy Lab (docs/assets/04_LAYOUT_SYSTEM.md — "Strategy Lab
 * Layout": Overview -> Tyre Strategy -> Pit Windows -> Undercut
 * Analysis -> Overcut Analysis -> Simulation -> Conclusion). Backed by
 * `/api/v1/races/{id}/strategy`, `/api/v1/races/{id}/pitstops`, and
 * `/api/v1/strategy/tyres` (docs/08_API_SPECIFICATION.md — "Strategy").
 *
 * Only tyre degradation/effectiveness and tyre-stint strategy are real
 * here. "Pit windows" drops the sample data's fabricated "optimal
 * window" comparison (no such model exists) and shows real pit stops
 * instead — currently empty for most races, the same documented
 * `fct_pitstop` gap seen on Race Playback. "Undercut analysis", "Overcut
 * analysis", and "Strategy simulation" stay permanent `loading`
 * placeholders: none of the three has *any* data source in this
 * pipeline (docs/08 explicitly scopes them out — they need pit-stop
 * timing more complete than Phase 4's gap allows, or a prediction model
 * that doesn't exist), the same treatment as "Telemetry" on Driver
 * Dossier.
 */
export function StrategyLabPage() {
  const [selectedId, setSelectedId] = useState<string | undefined>(undefined);

  const racesQuery = useRaces({ limit: 100 });
  const races = racesQuery.data?.data ?? [];
  const raceId = selectedId ?? races[0]?.id;
  const selectedRace = races.find((race) => race.id === raceId);

  const strategyQuery = useRaceStrategy(raceId);
  const driverStrategies = strategyQuery.data ?? [];
  const pitstopsQuery = useRacePitstops(raceId);
  const pitstops = pitstopsQuery.data ?? [];

  const degradationQuery = useTyreDegradation(
    selectedRace
      ? { season: selectedRace.season, race: selectedRace.round, session: RACE_SESSION_TYPE }
      : undefined,
  );
  const degradationPoints = degradationQuery.data?.points ?? [];
  const degradationChart = buildDegradationSeries(degradationPoints);
  const effectiveness = computeCompoundEffectiveness(degradationPoints);

  const fastestCompound = effectiveness[0];
  const slowestCompound = effectiveness[effectiveness.length - 1];
  const sampleLaps = degradationPoints.reduce((sum, point) => sum + point.sampleCount, 0);

  return (
    <>
      <Hero
        eyebrow="Strategy Lab"
        title={selectedRace?.raceName ?? "Loading race…"}
        {...(selectedRace?.circuit !== undefined && selectedRace?.circuit !== null
          ? { description: selectedRace.circuit }
          : {})}
        stats={[
          { label: "Fastest compound", value: fastestCompound?.compound ?? "—" },
          { label: "Slowest compound", value: slowestCompound?.compound ?? "—" },
          { label: "Compounds analyzed", value: String(effectiveness.length) },
          { label: "Sample laps", value: String(sampleLaps) },
        ]}
      />

      <Container className="flex flex-col gap-8 pb-(--section-gap)">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <Select
            label="Race"
            {...(raceId !== undefined && { value: raceId })}
            onValueChange={setSelectedId}
            options={races.map((item) => ({
              value: item.id,
              label: item.raceName ?? `Round ${item.round}`,
            }))}
            className="min-w-64"
          />
        </div>

        <WidgetGrid>
          <Widget
            title="Tyre strategy"
            description="Stint-by-stint compound choices for each driver."
            loading={strategyQuery.isPending}
            className="sm:col-span-2 laptop:col-span-12"
          >
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 laptop:grid-cols-3">
              {driverStrategies.map((driver) => (
                <div key={driver.driver} className="flex flex-col gap-2">
                  <span className="text-caption uppercase tracking-wide text-text-muted">
                    {driver.driver}
                  </span>
                  <ol className="flex flex-col gap-2">
                    {driver.stints.map((stint) => (
                      <li
                        key={`${stint.compound}-${stint.startLap}`}
                        className="flex items-center justify-between gap-3 border-b border-border-subtle pb-2 last:border-b-0 last:pb-0"
                      >
                        <Badge variant={resolveCompoundBadgeVariant(stint.compound)}>
                          {stint.compound ?? "Unknown"}
                        </Badge>
                        <span className="font-mono text-caption tabular-nums text-text-muted">
                          L{stint.startLap}–{stint.endLap}
                        </span>
                        <span className="text-body-sm text-text-secondary">
                          {stint.lapCount} laps
                        </span>
                      </li>
                    ))}
                  </ol>
                </div>
              ))}
            </div>
          </Widget>

          <Widget
            title="Pit windows"
            description="Actual pit stops this race, in order."
            loading={pitstopsQuery.isPending}
            className="laptop:col-span-6"
          >
            <ol className="flex flex-col gap-3">
              {pitstops.map((stop, index) => (
                <li
                  key={`${stop.driver}-${index}`}
                  className="flex items-center justify-between gap-3 border-b border-border-subtle pb-2 last:border-b-0 last:pb-0"
                >
                  <span className="text-body-sm text-text-primary">
                    {stop.driver} · Lap {stop.lap}
                  </span>
                  <span className="font-mono text-caption tabular-nums text-text-muted">
                    {stop.pitDuration != null ? `${stop.pitDuration.toFixed(1)}s` : "—"}
                  </span>
                </li>
              ))}
            </ol>
          </Widget>

          <Widget
            title="Tyre degradation"
            description="Pace loss per compound as tyre life increases."
            loading={degradationQuery.isPending}
            className="laptop:col-span-6"
          >
            <LineChart
              categories={degradationChart.categories}
              series={degradationChart.series.map((entry) => ({
                name: entry.compound,
                data: entry.data,
              }))}
              xAxisLabel="Tyre life (laps)"
              yAxisLabel="s"
              valueFormatter={(value) => `${value.toFixed(2)}s`}
              ariaLabel={`${selectedRace?.raceName ?? "Race"} tyre degradation by compound`}
            />
          </Widget>

          <Widget
            title="Undercut analysis"
            description="Net time gained or lost attempting the undercut."
            loading
            className="laptop:col-span-6"
          />

          <Widget
            title="Overcut analysis"
            description="Net time gained or lost attempting the overcut."
            loading
            className="laptop:col-span-6"
          />

          <Widget
            title="Compound effectiveness"
            description="Average lap pace by compound across the field."
            loading={degradationQuery.isPending}
            className="laptop:col-span-6"
          >
            <BarChart
              categories={effectiveness.map((entry) => entry.compound)}
              series={[
                { name: "Avg pace", data: effectiveness.map((entry) => entry.averageLapTime) },
              ]}
              yAxisLabel="Seconds"
              valueFormatter={(value) => `${value.toFixed(1)}s`}
              ariaLabel={`${selectedRace?.raceName ?? "Race"} compound effectiveness`}
            />
          </Widget>

          <Widget
            title="Strategy simulation"
            description="Precomputed candidate strategies compared by total race time."
            loading
            className="sm:col-span-2 laptop:col-span-12"
          />
        </WidgetGrid>
      </Container>
    </>
  );
}
