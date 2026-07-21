import {
  AreaChart,
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
 * The team selector here also drives the *global* constructor theme
 * (docs/01_PRODUCT_REQUIREMENTS.md Journey 2: "User selects Ferrari ->
 * entire interface adapts to Ferrari branding -> charts adopt Ferrari
 * theme"). That's why the charts on this page pass no explicit colors:
 * they inherit the active theme, which this page keeps in sync with the
 * selected team. Selection is initialized *from* the active theme so
 * arriving with McLaren branding shows McLaren, not a hardcoded default —
 * done in an effect (rather than a lazy `useState` initializer, like the
 * old sample-data version used) since the real team list only exists once
 * `useConstructors` has loaded.
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

      <Container className="flex flex-col gap-8 pb-(--section-gap)">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <Select
            label="Constructor"
            {...(constructorId !== undefined && { value: constructorId })}
            onValueChange={handleSelect}
            options={constructors.map((item) => ({ value: item.id, label: item.teamName }))}
            className="min-w-64"
          />
        </div>

        <WidgetGrid>
          <Widget
            title="Season performance"
            description="Championship points after each round."
            loading={resultsLoading}
            className="sm:col-span-2 laptop:col-span-12"
          >
            {resultsError ? (
              <QueryError />
            ) : (
              <AreaChart
                categories={races.map((race) => `R${race.round}`)}
                series={[{ name: team?.teamName ?? "Team", data: cumulativePoints }]}
                yAxisLabel="Points"
                valueFormatter={(value) => `${value} pts`}
                ariaLabel={`${team?.teamName ?? "Constructor"} championship points progression`}
              />
            )}
          </Widget>

          <Widget
            title="Pit stop efficiency"
            description="Average stationary time per season — lower is better."
            loading={performanceQuery.isPending}
            className="laptop:col-span-6"
          >
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
          </Widget>

          <Widget
            title="Driver comparison"
            description="Points scored per round by each driver."
            loading={resultsLoading || driversQuery.isPending}
            className="laptop:col-span-6"
          >
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
          </Widget>

          <Widget
            title="Reliability"
            description="Season reliability record."
            loading={statisticsQuery.isPending}
            className="laptop:col-span-6"
          >
            {statisticsQuery.isError ? (
              <QueryError />
            ) : (
              <dl className="flex flex-col gap-3">
                <ReliabilityRow
                  label="Seasons competed"
                  value={statistics ? String(statistics.seasonsCompeted) : "—"}
                />
                <ReliabilityRow
                  label="DNF rate"
                  value={
                    statistics?.dnfRate != null ? `${(statistics.dnfRate * 100).toFixed(0)}%` : "—"
                  }
                />
                <ReliabilityRow
                  label="Avg. points per race"
                  value={
                    statistics?.averagePoints != null ? statistics.averagePoints.toFixed(1) : "—"
                  }
                />
              </dl>
            )}
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
