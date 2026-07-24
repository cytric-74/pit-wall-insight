import {
  AreaChart,
  BarChart,
  Container,
  Hero,
  InstrumentGauge,
  isConstructorId,
  LineChart,
  Section,
  Select,
  Stat,
  useConstructorTheme,
} from "@pit-wall-insight/ui";
import { useEffect, useState } from "react";

import { resolveConstructorId } from "../../lib/constructor-id.js";
import { QueryError } from "../../lib/query-error.js";
import { useCurrentSeasonRaces } from "../races/queries.js";
import { useSessionResultsForRaces } from "../sessions/queries.js";
import {
  useConstructor,
  useConstructorDrivers,
  useConstructorPerformance,
  useConstructors,
  useConstructorStatistics,
} from "./queries.js";
import {
  cumulativeSum,
  extractDriverPointsByRound,
  extractTeamPointsByRound,
  hasPitstopAverage,
} from "./utils.js";

/**
 * Constructor Intelligence (docs/assets/04_LAYOUT_SYSTEM.md — layout
 * order: Constructor Overview -> Season Performance -> Reliability ->
 * Pit Strategy -> Development Trend -> Driver Comparison). Backed by
 * `/api/v1/constructors/*` (docs/08_API_SPECIFICATION.md — "Constructors").
 *
 * Editorial rebuild: "Season performance" is the one primary, full-width
 * analytical focus. Pit stop efficiency (a genuine per-season trend) and
 * driver comparison are demoted into a single secondary "Team form"
 * section. "Reliability" drops its `<dl>` rows for an `InstrumentGauge` —
 * DNF rate is exactly the single-dimension "where does this sit between
 * two ends" reading the gauge exists for. "Strategy tendencies" — a
 * permanent fake-loading placeholder with no data source on this page —
 * becomes a plain pointer to Strategy Lab instead.
 *
 * The team selector here also drives the *global* constructor theme
 * (docs/01_PRODUCT_REQUIREMENTS.md Journey 2: "User selects Ferrari ->
 * entire interface adapts to Ferrari branding -> charts adopt Ferrari
 * theme") — the Hero's ambient glow already picks up that accent via
 * `--color-constructor-glow`, which is this page's "team color wash"
 * rather than a fabricated car illustration (no real constructor SVGs
 * exist yet; see the redesign brief's media pipeline). Selection is
 * initialized *from* the active theme so arriving with McLaren branding
 * shows McLaren, not a hardcoded default.
 */
export function ConstructorIntelligencePage() {
  const { constructorId: activeThemeId, setConstructor } = useConstructorTheme();
  const [selectedId, setSelectedId] = useState<string | undefined>(undefined);

  const constructorsQuery = useConstructors({ limit: 100 });
  const constructors = constructorsQuery.data?.data ?? [];

  useEffect(() => {
    if (selectedId !== undefined || constructors.length === 0) return;
    const matching = constructors.find(
      (item) => resolveConstructorId(item.teamName) === activeThemeId,
    );
    setSelectedId((matching ?? constructors[0])?.id);
    // Deliberately keyed on `constructors.length` only (not `constructors`/
    // `activeThemeId`) — this should run once, when the list first arrives,
    // not on every subsequent render; re-running on `activeThemeId` would
    // fight the user's own later selection.
  }, [constructors.length]);

  const constructorId = selectedId ?? constructors[0]?.id;
  const constructorQuery = useConstructor(constructorId);
  const team = constructorQuery.data;
  const statisticsQuery = useConstructorStatistics(constructorId);
  const statistics = statisticsQuery.data;
  const performanceQuery = useConstructorPerformance(constructorId);
  const performance = performanceQuery.data ?? [];
  const driversQuery = useConstructorDrivers(constructorId);
  const rosterDrivers = driversQuery.data ?? [];

  const racesQuery = useCurrentSeasonRaces();
  const races = racesQuery.data ?? [];
  const resultsQueries = useSessionResultsForRaces(races);
  const resultsLoading = resultsQueries.some((query) => query.isPending);
  const resultsError = racesQuery.isError || resultsQueries.some((query) => query.isError);

  const driverNames = rosterDrivers.map((driver) => driver.fullName);
  const teamPointsPerRound = extractTeamPointsByRound(races, resultsQueries, driverNames);
  const cumulativePoints = cumulativeSum(teamPointsPerRound);
  const driverPointsPerRound = extractDriverPointsByRound(races, resultsQueries, driverNames);

  const pitStopRows = performance.filter(hasPitstopAverage);
  const dnfRatePercent = statistics?.dnfRate != null ? statistics.dnfRate * 100 : null;

  function handleSelect(id: string) {
    setSelectedId(id);
    const picked = constructors.find((item) => item.id === id);
    const slug = resolveConstructorId(picked?.teamName);
    if (isConstructorId(slug)) {
      setConstructor(slug);
    }
  }

  return (
    <>
      <Hero
        eyebrow="Constructor Intelligence"
        title={
          constructorQuery.isError
            ? "Couldn't load constructor"
            : (team?.teamName ?? "Loading constructor…")
        }
        {...(team?.baseCountry !== undefined && team?.baseCountry !== null
          ? { description: team.baseCountry }
          : {})}
        stats={[
          { label: "Wins", value: statistics ? String(statistics.wins) : "—" },
          { label: "Podiums", value: statistics ? String(statistics.podiums) : "—" },
          {
            label: "Avg. points",
            value: statistics?.averagePoints != null ? statistics.averagePoints.toFixed(1) : "—",
          },
        ]}
      />

      <Container className="flex flex-wrap items-end justify-between gap-4 py-8">
        <Select
          label="Constructor"
          {...(constructorId !== undefined && { value: constructorId })}
          onValueChange={handleSelect}
          options={constructors.map((item) => ({ value: item.id, label: item.teamName }))}
          className="min-w-64"
        />
      </Container>

      <Section title="Season performance" description="Championship points after each round.">
        {resultsError ? (
          <QueryError />
        ) : (
          <AreaChart
            categories={races.map((race) => `R${race.round}`)}
            series={[{ name: team?.teamName ?? "Team", data: cumulativePoints }]}
            yAxisLabel="Points"
            valueFormatter={(value) => `${value} pts`}
            ariaLabel={`${team?.teamName ?? "Constructor"} championship points progression`}
            height={400}
          />
        )}
      </Section>

      <Section title="Team form" description="Pit stop trend and driver contribution this season.">
        <div className="grid grid-cols-1 gap-x-16 gap-y-10 laptop:grid-cols-2">
          <div className="flex flex-col gap-4">
            <h3 className="font-mono text-caption uppercase tracking-wide text-text-muted">
              Pit stop efficiency
            </h3>
            {performanceQuery.isError ? (
              <QueryError />
            ) : (
              <LineChart
                categories={pitStopRows.map((entry) => String(entry.season))}
                series={[
                  {
                    name: team?.teamName ?? "Team",
                    data: pitStopRows.map((entry) => entry.pitstopAverage),
                  },
                ]}
                yAxisLabel="Seconds"
                valueFormatter={(value) => `${value.toFixed(1)}s`}
                ariaLabel={`${team?.teamName ?? "Constructor"} average pit stop time per season`}
              />
            )}
          </div>

          <div className="flex flex-col gap-4">
            <h3 className="font-mono text-caption uppercase tracking-wide text-text-muted">
              Driver comparison
            </h3>
            {resultsError || driversQuery.isError ? (
              <QueryError />
            ) : (
              <BarChart
                categories={races.map((race) => `R${race.round}`)}
                series={driverPointsPerRound.map((entry) => ({
                  name: entry.driver,
                  data: entry.points,
                }))}
                yAxisLabel="Points"
                valueFormatter={(value) => `${value} pts`}
                ariaLabel={`${team?.teamName ?? "Constructor"} driver points comparison`}
              />
            )}
          </div>
        </div>
        {resultsLoading ? (
          <p className="mt-6 font-mono text-caption uppercase tracking-wide text-text-muted">
            Syncing telemetry…
          </p>
        ) : null}
      </Section>

      <Section title="Reliability" description="Season reliability record.">
        {statisticsQuery.isError ? (
          <QueryError />
        ) : (
          <div className="grid grid-cols-1 items-start gap-x-16 gap-y-10 laptop:grid-cols-[minmax(0,1fr)_280px]">
            <InstrumentGauge
              label="DNF rate"
              value={dnfRatePercent ?? 0}
              minLabel="Reliable"
              maxLabel="DNF-prone"
              {...(dnfRatePercent != null && { valueLabel: `${dnfRatePercent.toFixed(0)}%` })}
            />
            <div className="flex flex-col gap-8 border-t border-border-subtle pt-8 laptop:border-l laptop:border-t-0 laptop:pl-12 laptop:pt-0">
              <Stat
                label="Seasons competed"
                value={statistics ? statistics.seasonsCompeted : "—"}
              />
              <Stat
                label="Avg. points per race"
                value={
                  statistics?.averagePoints != null ? statistics.averagePoints.toFixed(1) : "—"
                }
              />
            </div>
          </div>
        )}

        <p className="mt-10 font-mono text-caption uppercase tracking-wide text-text-muted">
          Stint lengths, compound choices, and pit windows —{" "}
          <a
            href="/strategy"
            className="text-constructor-primary transition-colors duration-(--duration-fast) ease-standard hover:text-accent-hover"
          >
            Strategy Lab
          </a>
        </p>
      </Section>
    </>
  );
}
