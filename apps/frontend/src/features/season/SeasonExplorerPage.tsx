import {
  AreaChart,
  Badge,
  BarChart,
  Container,
  getConstructorTheme,
  Hero,
  LineChart,
  Select,
  Widget,
  WidgetGrid,
} from "@pit-wall-insight/ui";
import { useState } from "react";

import { getSampleSeason, SAMPLE_ROUNDS, SAMPLE_SEASONS } from "./data.js";

const DEFAULT_SEASON_ID = SAMPLE_SEASONS[0]!.id;

/**
 * Season Explorer (docs/01_PRODUCT_REQUIREMENTS.md: standings
 * progression, team evolution, driver evolution, constructor dominance,
 * race calendar, championship battles). There is no dedicated "Season
 * Explorer Layout" section in docs/assets/04_LAYOUT_SYSTEM.md — this
 * ordering is inferred from the product requirements and
 * docs/13_ROADMAP.md's Milestone 11 feature list instead. Runs on the
 * sample data in ./data.ts — visibly badged as such — until the season
 * endpoints exist.
 *
 * "Driver evolution" is covered by the championship progress chart
 * rather than a separate widget — it's the same cumulative-points data,
 * just per driver instead of per team.
 */
export function SeasonExplorerPage() {
  const [seasonId, setSeasonId] = useState<string>(DEFAULT_SEASON_ID);
  const season = getSampleSeason(seasonId) ?? SAMPLE_SEASONS[0]!;

  const driversByFinalPoints = [...season.driverStandings].sort(
    (a, b) => b.progression[b.progression.length - 1]! - a.progression[a.progression.length - 1]!,
  );
  const leader = driversByFinalPoints[0]!;
  const runnerUp = driversByFinalPoints[1]!;
  const leaderConstructor = [...season.constructorStandings].sort(
    (a, b) => b.progression[b.progression.length - 1]! - a.progression[a.progression.length - 1]!,
  )[0]!;
  const pointsGap =
    leader.progression[leader.progression.length - 1]! -
    runnerUp.progression[runnerUp.progression.length - 1]!;
  const gapTrend = leader.progression.map((points, index) => points - runnerUp.progression[index]!);

  return (
    <>
      <Hero
        eyebrow="Season Explorer"
        title={`${season.year} Season`}
        description={`${season.completed ? "Completed" : "In progress"} · ${SAMPLE_ROUNDS.length} rounds`}
        stats={[
          { label: season.completed ? "Champion" : "Leader", value: leader.driver },
          { label: "Leading team", value: leaderConstructor.name },
          { label: "Rounds", value: String(SAMPLE_ROUNDS.length) },
          { label: "Points gap", value: String(pointsGap) },
        ]}
      />

      <Container className="flex flex-col gap-8 pb-(--section-gap)">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <Select
            label="Season"
            value={seasonId}
            onValueChange={setSeasonId}
            options={SAMPLE_SEASONS.map((item) => ({ value: item.id, label: String(item.year) }))}
            className="min-w-48"
          />
          <Badge variant="warning">Sample data</Badge>
        </div>

        <WidgetGrid>
          <Widget
            title="Championship progress"
            description="Cumulative driver points after each round."
            className="sm:col-span-2 laptop:col-span-12"
          >
            <LineChart
              categories={SAMPLE_ROUNDS}
              series={season.driverStandings.map((driver) => {
                const teamColor = getConstructorTheme(driver.constructorId);
                return {
                  name: driver.abbreviation,
                  data: driver.progression,
                  ...(teamColor ? { color: teamColor.primary } : {}),
                };
              })}
              xAxisLabel="Round"
              yAxisLabel="Points"
              valueFormatter={(value) => `${value} pts`}
              ariaLabel={`${season.year} championship progress by driver, sample data`}
              height={360}
            />
          </Widget>

          <Widget
            title="Team evolution"
            description="Cumulative constructor points after each round."
            className="laptop:col-span-6"
          >
            <LineChart
              categories={SAMPLE_ROUNDS}
              series={season.constructorStandings.map((team) => {
                const teamColor = getConstructorTheme(team.constructorId);
                return {
                  name: team.name,
                  data: team.progression,
                  ...(teamColor ? { color: teamColor.primary } : {}),
                };
              })}
              yAxisLabel="Points"
              valueFormatter={(value) => `${value} pts`}
              ariaLabel={`${season.year} team evolution, sample data`}
            />
          </Widget>

          <Widget
            title="Championship battle"
            description={`Points gap between ${leader.abbreviation} and ${runnerUp.abbreviation}.`}
            className="laptop:col-span-6"
          >
            <AreaChart
              categories={SAMPLE_ROUNDS}
              series={[{ name: "Gap", data: gapTrend }]}
              yAxisLabel="Points"
              valueFormatter={(value) => `${value} pts`}
              ariaLabel={`${season.year} championship battle points gap, sample data`}
            />
          </Widget>

          <Widget
            title="Constructor dominance"
            description="Race wins by constructor this season."
            className="laptop:col-span-6"
          >
            <BarChart
              categories={season.constructorStandings.map((team) => team.name)}
              series={[
                {
                  name: "Wins",
                  data: season.constructorStandings.map((team) => team.wins),
                },
              ]}
              yAxisLabel="Wins"
              ariaLabel={`${season.year} constructor dominance by wins, sample data`}
            />
          </Widget>

          <Widget
            title="Race calendar"
            description="Round-by-round results for this season."
            className="laptop:col-span-6"
          >
            <ol className="flex flex-col gap-2">
              {season.calendar.map((race) => (
                <li
                  key={race.round}
                  className="flex items-center justify-between gap-3 border-b border-border-subtle pb-2 last:border-b-0 last:pb-0"
                >
                  <span className="flex items-center gap-3">
                    <span className="font-mono text-caption uppercase tracking-wide text-text-muted">
                      {race.round}
                    </span>
                    <span className="text-body-sm text-text-primary">{race.name}</span>
                  </span>
                  <span className="text-caption text-text-muted">{race.winner}</span>
                </li>
              ))}
            </ol>
          </Widget>
        </WidgetGrid>
      </Container>
    </>
  );
}
