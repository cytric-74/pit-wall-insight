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
import type { BadgeProps } from "@pit-wall-insight/ui";
import { useState } from "react";

import type { Compound } from "./data.js";
import { getSampleStrategy, SAMPLE_STRATEGIES, STINT_LAP_MARKERS } from "./data.js";

const DEFAULT_RACE_ID = SAMPLE_STRATEGIES[0]!.id;

/**
 * Matches real tyre compound coloring (soft = red, medium = yellow,
 * hard = white) using the existing Badge semantic variants rather than
 * introducing compound-specific colors.
 */
const COMPOUND_BADGE_VARIANT: Record<Compound, NonNullable<BadgeProps["variant"]>> = {
  Soft: "danger",
  Medium: "warning",
  Hard: "neutral",
};

/**
 * Strategy Lab (docs/assets/04_LAYOUT_SYSTEM.md — "Strategy Lab
 * Layout": Overview -> Tyre Strategy -> Pit Windows -> Undercut
 * Analysis -> Overcut Analysis -> Simulation -> Conclusion, "users
 * should naturally move from observation to understanding"). Runs on
 * the sample data in ./data.ts — visibly badged as such — until the
 * strategy endpoints (`fct_strategy`, `fct_pitstop`) exist.
 *
 * Scope note: docs/13_ROADMAP.md calls the full "Strategy Simulator" an
 * interactive strategy builder and lists it as a future milestone goal,
 * not this one. The "Simulation" widget below shows two precomputed
 * candidate strategies rather than a free-form builder; its description
 * carries the doc's "Conclusion" step (which strategy comes out ahead)
 * instead of a separate widget.
 */
export function StrategyLabPage() {
  const [raceId, setRaceId] = useState<string>(DEFAULT_RACE_ID);
  const strategy = getSampleStrategy(raceId) ?? SAMPLE_STRATEGIES[0]!;

  const bestSimulation = [...strategy.simulations].sort(
    (a, b) => a.totalRaceTimeSeconds - b.totalRaceTimeSeconds,
  )[0]!;
  const worstSimulation = [...strategy.simulations].sort(
    (a, b) => b.totalRaceTimeSeconds - a.totalRaceTimeSeconds,
  )[0]!;
  const simulatedGain = worstSimulation.totalRaceTimeSeconds - bestSimulation.totalRaceTimeSeconds;
  const fastestCompound = [...strategy.compoundEffectiveness].sort(
    (a, b) => a.averagePaceSeconds - b.averagePaceSeconds,
  )[0]!;
  const totalPitStops = strategy.drivers.reduce((sum, driver) => sum + driver.pitStops.length, 0);

  return (
    <>
      <Hero
        eyebrow="Strategy Lab"
        title={strategy.raceName}
        description={`${strategy.circuit} · ${strategy.laps} laps`}
        stats={[
          { label: "Pit stops", value: String(totalPitStops) },
          { label: "Fastest compound", value: fastestCompound.compound },
          { label: "Best strategy", value: bestSimulation.label },
          { label: "Simulated gain", value: simulatedGain.toFixed(1), unit: "s" },
        ]}
      />

      <Container className="flex flex-col gap-8 pb-(--section-gap)">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <Select
            label="Race"
            value={raceId}
            onValueChange={setRaceId}
            options={SAMPLE_STRATEGIES.map((item) => ({ value: item.id, label: item.raceName }))}
            className="min-w-64"
          />
          <Badge variant="warning">Sample data</Badge>
        </div>

        <WidgetGrid>
          <Widget
            title="Tyre strategy"
            description="Stint-by-stint compound choices for each driver."
            className="sm:col-span-2 laptop:col-span-12"
          >
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 laptop:grid-cols-3">
              {strategy.drivers.map((driver) => (
                <div key={driver.abbreviation} className="flex flex-col gap-2">
                  <span className="text-caption uppercase tracking-wide text-text-muted">
                    {driver.driver}
                  </span>
                  <ol className="flex flex-col gap-2">
                    {driver.stints.map((stint) => (
                      <li
                        key={`${stint.compound}-${stint.startLap}`}
                        className="flex items-center justify-between gap-3 border-b border-border-subtle pb-2 last:border-b-0 last:pb-0"
                      >
                        <Badge variant={COMPOUND_BADGE_VARIANT[stint.compound]}>
                          {stint.compound}
                        </Badge>
                        <span className="font-mono text-caption tabular-nums text-text-muted">
                          L{stint.startLap}–{stint.endLap}
                        </span>
                        <span className="text-body-sm text-text-secondary">
                          {stint.averagePace.toFixed(1)}s
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
            description="Actual stop lap vs. the modeled optimal window."
            className="laptop:col-span-6"
          >
            <ol className="flex flex-col gap-3">
              {strategy.drivers.flatMap((driver) =>
                driver.pitStops.map((stop, index) => {
                  const inWindow =
                    stop.lap >= stop.optimalWindow[0] && stop.lap <= stop.optimalWindow[1];
                  return (
                    <li
                      key={`${driver.abbreviation}-${index}`}
                      className="flex items-center justify-between gap-3 border-b border-border-subtle pb-2 last:border-b-0 last:pb-0"
                    >
                      <span className="text-body-sm text-text-primary">
                        {driver.abbreviation} · Lap {stop.lap}
                      </span>
                      <span className="font-mono text-caption tabular-nums text-text-muted">
                        Window {stop.optimalWindow[0]}–{stop.optimalWindow[1]}
                      </span>
                      <Badge variant={inWindow ? "success" : "warning"}>
                        {inWindow ? "In window" : "Off window"}
                      </Badge>
                    </li>
                  );
                }),
              )}
            </ol>
          </Widget>

          <Widget
            title="Tyre degradation"
            description="Pace loss per compound as a stint progresses."
            className="laptop:col-span-6"
          >
            <LineChart
              categories={STINT_LAP_MARKERS}
              series={Object.entries(strategy.degradationByCompound).map(([compound, data]) => ({
                name: compound,
                data,
              }))}
              xAxisLabel="Laps into stint"
              yAxisLabel="s"
              valueFormatter={(value) => `+${value.toFixed(2)}s`}
              ariaLabel={`${strategy.raceName} tyre degradation by compound, sample data`}
            />
          </Widget>

          <Widget
            title="Undercut analysis"
            description="Net time gained or lost attempting the undercut."
            className="laptop:col-span-6"
          >
            <BarChart
              categories={strategy.undercuts.map((attempt) => attempt.label)}
              series={[
                {
                  name: "Net gain",
                  data: strategy.undercuts.map((attempt) => attempt.netGainSeconds),
                },
              ]}
              yAxisLabel="Seconds"
              valueFormatter={(value) => `${value.toFixed(1)}s`}
              ariaLabel={`${strategy.raceName} undercut analysis, sample data`}
            />
          </Widget>

          <Widget
            title="Overcut analysis"
            description="Net time gained or lost attempting the overcut."
            className="laptop:col-span-6"
          >
            <BarChart
              categories={strategy.overcuts.map((attempt) => attempt.label)}
              series={[
                {
                  name: "Net gain",
                  data: strategy.overcuts.map((attempt) => attempt.netGainSeconds),
                },
              ]}
              yAxisLabel="Seconds"
              valueFormatter={(value) => `${value.toFixed(1)}s`}
              ariaLabel={`${strategy.raceName} overcut analysis, sample data`}
            />
          </Widget>

          <Widget
            title="Compound effectiveness"
            description="Average lap pace by compound across the field."
            className="laptop:col-span-6"
          >
            <BarChart
              categories={strategy.compoundEffectiveness.map((entry) => entry.compound)}
              series={[
                {
                  name: "Avg pace",
                  data: strategy.compoundEffectiveness.map((entry) => entry.averagePaceSeconds),
                },
              ]}
              yAxisLabel="Seconds"
              valueFormatter={(value) => `${value.toFixed(1)}s`}
              ariaLabel={`${strategy.raceName} compound effectiveness, sample data`}
            />
          </Widget>

          <Widget
            title="Strategy simulation"
            description={`${bestSimulation.label} beats ${worstSimulation.label} by ${simulatedGain.toFixed(1)}s over the race.`}
            className="sm:col-span-2 laptop:col-span-12"
          >
            <BarChart
              categories={strategy.simulations.map((simulation) => simulation.label)}
              series={[
                {
                  name: "Total race time",
                  data: strategy.simulations.map((simulation) => simulation.totalRaceTimeSeconds),
                },
              ]}
              yAxisLabel="Seconds"
              valueFormatter={(value) => `${(value / 60).toFixed(1)} min`}
              ariaLabel={`${strategy.raceName} strategy simulation comparison, sample data`}
            />
          </Widget>
        </WidgetGrid>
      </Container>
    </>
  );
}
