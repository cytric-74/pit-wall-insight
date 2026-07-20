import {
  BarChart,
  Container,
  formatTemperature,
  getConstructorTheme,
  Hero,
  LineChart,
  Select,
  usePreferences,
  Widget,
  WidgetGrid,
} from "@pit-wall-insight/ui";
import { useState } from "react";

import { resolveConstructorId } from "../../lib/constructor-id.js";
import { EmptyState } from "../../lib/empty-state.js";
import { QueryError } from "../../lib/query-error.js";
import { useSessionResults } from "../sessions/queries.js";
import {
  useRace,
  useRacePitstops,
  useRacePositions,
  useRaces,
  useRaceStrategy,
  useRaceWeather,
} from "./queries.js";
import { buildPositionSeries, buildStrategyEvents, estimateRaceLaps } from "./utils.js";

/**
 * Race Playback (docs/assets/04_LAYOUT_SYSTEM.md — "Race Playback
 * Layout": Race Context -> Timeline -> Playback Controls -> Live
 * Analytics -> Race Events -> Driver Tracking). Backed by
 * `/api/v1/races/*` (docs/08_API_SPECIFICATION.md — "Races").
 *
 * Scope note: this implements the analytics half of that layout (position
 * changes, weather, pit stops, the event timeline, final classification).
 * The doc's "Playback Controls" — scrubbing lap-by-lap with synchronized
 * telemetry — needs a dedicated timeline/scrubber component (and
 * telemetry data) that don't exist; it isn't attempted here.
 *
 * "Weather evolution" became a single snapshot, not a per-lap chart —
 * `dim_weather` is one aggregated row per session (see
 * `@pit-wall-insight/shared-types`'s `RaceWeather` docstring), so there is
 * no lap-indexed series to plot. "Race events" reinterprets tyre-stint
 * changes as the timeline, since no safety car/VSC log exists anywhere in
 * this pipeline — labeled honestly as tyre changes, not fabricated
 * incidents.
 *
 * Each driver's line in "Position changes" keeps their own constructor's
 * color (resolved from `/sessions/{id}/results`, the only endpoint that
 * pairs a driver with a team for this race) rather than the global theme,
 * since a single race mixes drivers from several teams.
 */
export function RacePlaybackPage() {
  const [selectedId, setSelectedId] = useState<string | undefined>(undefined);

  const racesQuery = useRaces({ limit: 100 });
  const races = racesQuery.data?.data ?? [];
  const raceId = selectedId ?? races[0]?.id;

  const raceQuery = useRace(raceId);
  const race = raceQuery.data;
  const positionsQuery = useRacePositions(raceId);
  const positions = positionsQuery.data ?? [];
  const pitstopsQuery = useRacePitstops(raceId);
  const pitstops = pitstopsQuery.data ?? [];
  const weatherQuery = useRaceWeather(raceId);
  const weather = weatherQuery.data;
  const strategyQuery = useRaceStrategy(raceId);
  const strategyEvents = buildStrategyEvents(strategyQuery.data ?? []);

  const resultsQuery = useSessionResults(raceId);
  const results = resultsQuery.data ?? [];
  const teamByDriver = new Map(results.map((entry) => [entry.driver, entry.team]));

  const { preferences } = usePreferences();
  const temperatureUnitLabel = preferences.temperatureUnit === "fahrenheit" ? "°F" : "°C";

  const positionChart = buildPositionSeries(positions);
  const estimatedLaps = estimateRaceLaps(positions);

  const finalClassification = [...results].sort((a, b) => {
    if (a.finishPosition == null) return 1;
    if (b.finishPosition == null) return -1;
    return a.finishPosition - b.finishPosition;
  });

  return (
    <>
      <Hero
        eyebrow="Race Playback"
        title={raceQuery.isError ? "Couldn't load race" : (race?.raceName ?? "Loading race…")}
        description={[
          race?.circuit,
          race?.date,
          estimatedLaps !== undefined ? `${estimatedLaps} laps` : null,
        ]
          .filter((part): part is string => Boolean(part))
          .join(" · ")}
        stats={[
          { label: "Winner", value: race?.winner ?? "—" },
          { label: "Pole", value: race?.pole ?? "—" },
          { label: "Fastest lap", value: race?.fastestLap ?? "—" },
          {
            label: "Retirements",
            value: race?.retirements != null ? String(race.retirements) : "—",
          },
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
            title="Position changes"
            description="Race position after each lap — lower is better."
            loading={positionsQuery.isPending}
            className="sm:col-span-2 laptop:col-span-12"
          >
            {positionsQuery.isError ? (
              <QueryError />
            ) : (
              <LineChart
                categories={positionChart.categories}
                series={positionChart.series.map((entry) => {
                  const teamColor = getConstructorTheme(
                    resolveConstructorId(teamByDriver.get(entry.driver)),
                  );
                  return {
                    name: entry.driver,
                    data: entry.data,
                    ...(teamColor ? { color: teamColor.primary } : {}),
                  };
                })}
                yAxisLabel="Position"
                yAxisInverse
                valueFormatter={(value) => `P${value}`}
                ariaLabel={`${race?.raceName ?? "Race"} position changes by lap`}
              />
            )}
          </Widget>

          <Widget
            title="Weather"
            description="Track/air conditions for this session."
            loading={weatherQuery.isPending}
            className="laptop:col-span-6"
          >
            {weatherQuery.isError ? (
              <QueryError />
            ) : (
              <>
                <dl className="flex flex-col gap-3">
                  <WeatherRow
                    label="Track temperature"
                    value={
                      weather?.trackTemperature != null
                        ? formatTemperature(weather.trackTemperature, preferences.temperatureUnit)
                        : "—"
                    }
                  />
                  <WeatherRow
                    label="Air temperature"
                    value={
                      weather?.airTemperature != null
                        ? formatTemperature(weather.airTemperature, preferences.temperatureUnit)
                        : "—"
                    }
                  />
                  <WeatherRow
                    label="Rainfall"
                    value={weather?.rainfall == null ? "—" : weather.rainfall ? "Yes" : "No"}
                  />
                </dl>
                <p className="mt-3 text-caption text-text-muted">
                  Session average, in {temperatureUnitLabel} — not a per-lap trace.
                </p>
              </>
            )}
          </Widget>

          <Widget
            title="Pit stop timeline"
            description="Stationary time per stop, in order."
            loading={pitstopsQuery.isPending}
            className="laptop:col-span-6"
          >
            {pitstopsQuery.isError ? (
              <QueryError />
            ) : (
              <BarChart
                categories={pitstops.map((stop) => `${stop.driver} Lap ${stop.lap}`)}
                series={[{ name: "Duration", data: pitstops.map((stop) => stop.pitDuration ?? 0) }]}
                yAxisLabel="Seconds"
                valueFormatter={(value) => `${value.toFixed(1)}s`}
                ariaLabel={`${race?.raceName ?? "Race"} pit stop durations`}
              />
            )}
          </Widget>

          <Widget
            title="Race events"
            description="Tyre stint changes across the race."
            loading={strategyQuery.isPending}
            className="laptop:col-span-6"
          >
            {strategyQuery.isError ? (
              <QueryError />
            ) : strategyEvents.length === 0 ? (
              <EmptyState message="No race events found" />
            ) : (
              <ol className="flex flex-col gap-3">
                {strategyEvents.map((event, index) => (
                  <li key={`${event.lap}-${index}`} className="flex gap-3">
                    <span className="w-14 shrink-0 font-mono text-caption uppercase tracking-wide text-text-muted">
                      Lap {event.lap}
                    </span>
                    <span className="text-body-sm text-text-secondary">{event.label}</span>
                  </li>
                ))}
              </ol>
            )}
          </Widget>

          <Widget
            title="Driver tracking"
            description="Final classification for this race."
            loading={resultsQuery.isPending}
            className="laptop:col-span-6"
          >
            {resultsQuery.isError ? (
              <QueryError />
            ) : finalClassification.length === 0 ? (
              <EmptyState message="No results found" />
            ) : (
              <ol className="flex flex-col gap-2">
                {finalClassification.map((entry, index) => (
                  <li
                    key={entry.driver}
                    className="flex items-center justify-between border-b border-border-subtle pb-2 last:border-b-0 last:pb-0"
                  >
                    <span className="flex items-center gap-3">
                      <span className="font-mono text-caption tabular-nums text-text-muted">
                        P{index + 1}
                      </span>
                      <span className="text-body-sm text-text-primary">{entry.driver}</span>
                    </span>
                    <span className="font-mono text-caption uppercase tracking-wide text-text-muted">
                      {entry.team ?? "—"}
                    </span>
                  </li>
                ))}
              </ol>
            )}
          </Widget>
        </WidgetGrid>
      </Container>
    </>
  );
}

function WeatherRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between border-b border-border-subtle pb-3">
      <dt className="font-mono text-caption uppercase tracking-wide text-text-muted">{label}</dt>
      <dd className="font-mono text-body-md tabular-nums text-text-primary">{value}</dd>
    </div>
  );
}
