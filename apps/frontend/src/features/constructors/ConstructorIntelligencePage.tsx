import {
  AreaChart,
  Badge,
  BarChart,
  Container,
  Hero,
  isConstructorId,
  LineChart,
  Select,
  useConstructorTheme,
  Widget,
  WidgetGrid,
} from "@pit-wall-insight/ui";
import { useState } from "react";

import { SAMPLE_ROUNDS } from "../../constants/season.js";
import { getSampleConstructor, SAMPLE_CONSTRUCTORS } from "./data.js";

const DEFAULT_CONSTRUCTOR_ID = SAMPLE_CONSTRUCTORS[0]!.id;

/**
 * Constructor Intelligence (docs/assets/04_LAYOUT_SYSTEM.md — layout
 * order: Constructor Overview -> Season Performance -> Reliability ->
 * Pit Strategy -> Development Trend -> Driver Comparison). Runs on the
 * sample data in ./data.ts — visibly badged as such — until the
 * constructor endpoints exist.
 *
 * The team selector here also drives the *global* constructor theme
 * (docs/01_PRODUCT_REQUIREMENTS.md Journey 2: "User selects Ferrari ->
 * entire interface adapts to Ferrari branding -> charts adopt Ferrari
 * theme"). That's why the charts on this page pass no explicit colors:
 * they inherit the active theme, which this page keeps in sync with the
 * selected team. Selection is initialized *from* the active theme so
 * arriving with McLaren branding shows McLaren, not a hardcoded default.
 */
export function ConstructorIntelligencePage() {
  const { constructorId, setConstructor } = useConstructorTheme();
  const [selectedId, setSelectedId] = useState<string>(() =>
    constructorId && getSampleConstructor(constructorId) ? constructorId : DEFAULT_CONSTRUCTOR_ID,
  );
  const team = getSampleConstructor(selectedId) ?? SAMPLE_CONSTRUCTORS[0]!;

  function handleSelect(id: string) {
    setSelectedId(id);
    if (isConstructorId(id)) {
      setConstructor(id);
    }
  }

  return (
    <>
      <Hero
        eyebrow="Constructor Intelligence"
        title={team.name}
        description={`${team.base} · ${team.powerUnit} power unit`}
        stats={[
          { label: "Wins", value: String(team.stats.wins) },
          { label: "Podiums", value: String(team.stats.podiums) },
          { label: "Poles", value: String(team.stats.poles) },
          { label: "Points", value: String(team.stats.points) },
        ]}
      />

      <Container className="flex flex-col gap-8 pb-(--section-gap)">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <Select
            label="Constructor"
            value={selectedId}
            onValueChange={handleSelect}
            options={SAMPLE_CONSTRUCTORS.map((item) => ({ value: item.id, label: item.name }))}
            className="min-w-64"
          />
          <Badge variant="warning">Sample data</Badge>
        </div>

        <WidgetGrid>
          <Widget
            title="Season performance"
            description="Championship points after each round."
            className="sm:col-span-2 laptop:col-span-12"
          >
            <AreaChart
              categories={SAMPLE_ROUNDS}
              series={[{ name: team.name, data: team.cumulativePoints }]}
              yAxisLabel="Points"
              valueFormatter={(value) => `${value} pts`}
              ariaLabel={`${team.name} championship points progression, sample data`}
            />
          </Widget>

          <Widget
            title="Pit stop efficiency"
            description="Average stationary time per round — lower is better."
            className="laptop:col-span-6"
          >
            <LineChart
              categories={SAMPLE_ROUNDS}
              series={[{ name: team.name, data: team.averagePitStops }]}
              yAxisLabel="Seconds"
              valueFormatter={(value) => `${value.toFixed(1)}s`}
              ariaLabel={`${team.name} average pit stop time per round, sample data`}
            />
          </Widget>

          <Widget
            title="Driver comparison"
            description="Points scored per round by each driver."
            className="laptop:col-span-6"
          >
            <BarChart
              categories={SAMPLE_ROUNDS}
              series={team.drivers.map((driver) => ({
                name: driver.abbreviation,
                data: driver.pointsPerRound,
              }))}
              yAxisLabel="Points"
              valueFormatter={(value) => `${value} pts`}
              ariaLabel={`${team.name} driver points comparison, sample data`}
            />
          </Widget>

          <Widget
            title="Reliability"
            description="Finishing record this season."
            className="laptop:col-span-6"
          >
            <dl className="flex flex-col gap-3">
              <ReliabilityRow
                label="Classified finishes"
                value={team.reliability.classifiedFinishes}
              />
              <ReliabilityRow label="DNFs" value={String(team.reliability.dnfs)} />
              <ReliabilityRow label="Laps completed" value={team.reliability.lapsCompletedPct} />
            </dl>
          </Widget>

          <Widget
            title="Strategy tendencies"
            description="Stint lengths, compound choices, and pit windows"
            href="/strategy"
            linkLabel="Strategy Lab"
            loading
            className="laptop:col-span-6"
          />
        </WidgetGrid>
      </Container>
    </>
  );
}

function ReliabilityRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between border-b border-border-subtle pb-3">
      <dt className="font-mono text-caption uppercase tracking-wide text-text-muted">{label}</dt>
      <dd className="font-mono text-body-md tabular-nums text-text-primary">{value}</dd>
    </div>
  );
}
