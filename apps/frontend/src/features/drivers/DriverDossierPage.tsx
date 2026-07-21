import {
  BarChart,
  Container,
  getConstructorTheme,
  Hero,
  LineChart,
  Section,
  Select,
} from "@pit-wall-insight/ui";
import { useState } from "react";

import { resolveConstructorId } from "../../lib/constructor-id.js";
import { QueryError } from "../../lib/query-error.js";
import { useCurrentSeasonRaces } from "../races/queries.js";
import { useSessionResultsForRaces } from "../sessions/queries.js";
import {
  useDriver,
  useDriverLaps,
  useDrivers,
  useDriverStatistics,
  useTeammate,
} from "./queries.js";
import { buildPaceSeries, extractRoundPositions, hasFinish, hasGridAndFinish } from "./utils.js";

const RACE_SESSION_TYPE = "R";

/**
 * Driver Dossier (docs/assets/04_LAYOUT_SYSTEM.md — "Driver Dossier
 * Layout": Driver Overview -> Performance Summary -> Lap Analysis ->
 * Telemetry -> Race History -> Comparisons). Backed by `/api/v1/drivers/*`
 * (docs/08_API_SPECIFICATION.md — "Drivers").
 *
 * Editorial rebuild: the driver's number becomes a giant, low-opacity
 * watermark behind the Hero text instead of the generic circuit graphic
 * (see the redesign brief — "driver numbers become background graphics").
 * "Race pace" is the one primary analytical focus (full width, the actual
 * lap-analysis question this page exists to answer); qualifying-vs-race
 * and position progression are demoted into a single secondary "Season
 * form" section. "Telemetry" is no longer a permanent fake-loading
 * skeleton (there is no telemetry data source for this page — an
 * indefinite skeleton misrepresented that as "still loading"); it's a
 * plain pointer to Telemetry Center instead.
 *
 * Charts are colored with the *selected driver's* constructor colors
 * (explicit per-series override) rather than the global constructor
 * theme, so comparing drivers across teams always shows each driver in
 * their own team's color regardless of which theme the user picked.
 */
export function DriverDossierPage() {
  const [selectedDriverId, setSelectedDriverId] = useState<string | undefined>(undefined);

  const driversQuery = useDrivers({ limit: 100 });
  const drivers = driversQuery.data?.data ?? [];
  const driverId = selectedDriverId ?? drivers[0]?.id;

  const driverQuery = useDriver(driverId);
  const driver = driverQuery.data;
  const statisticsQuery = useDriverStatistics(driverId);
  const statistics = statisticsQuery.data;

  const teammateQuery = useTeammate(driver?.teamId ?? undefined, driverId);
  const teammate = teammateQuery.teammate;

  const racesQuery = useCurrentSeasonRaces();
  const races = racesQuery.data ?? [];
  const resultsQueries = useSessionResultsForRaces(races);
  const resultsLoading = resultsQueries.some((query) => query.isPending);
  const resultsError = racesQuery.isError || resultsQueries.some((query) => query.isError);
  const latestRace = races[races.length - 1];

  const driverLapsQuery = useDriverLaps(
    driverId,
    latestRace
      ? { season: latestRace.season, race: latestRace.round, session: RACE_SESSION_TYPE }
      : undefined,
  );
  const teammateLapsQuery = useDriverLaps(
    teammate?.id,
    latestRace
      ? { season: latestRace.season, race: latestRace.round, session: RACE_SESSION_TYPE }
      : undefined,
  );

  const teamColors = getConstructorTheme(resolveConstructorId(driver?.team));
  // Absent (not `undefined`) when the lookup misses, so charts fall back
  // to the active constructor theme rather than receiving color: undefined.
  const primaryColor = teamColors ? { color: teamColors.primary } : {};
  const secondaryColor = teamColors ? { color: teamColors.secondary } : {};

  const pace = buildPaceSeries(
    driverLapsQuery.data ?? [],
    teammate ? teammateLapsQuery.data : undefined,
  );

  const positions = driver ? extractRoundPositions(races, resultsQueries, driver.fullName) : [];
  const qualifyingVsRaceRows = positions.filter(hasGridAndFinish);
  const progressionRows = positions.filter(hasFinish);

  return (
    <>
      <Hero
        eyebrow="Driver Dossier"
        title={
          driverQuery.isError ? "Couldn't load driver" : (driver?.fullName ?? "Loading driver…")
        }
        description={[
          driver?.driverNumber != null ? `#${driver.driverNumber}` : null,
          driver?.team,
          driver?.nationality,
        ]
          .filter((part): part is string => Boolean(part))
          .join(" · ")}
        stats={[
          { label: "Wins", value: statistics ? String(statistics.wins) : "—" },
          { label: "Podiums", value: statistics ? String(statistics.podiums) : "—" },
          { label: "Poles", value: statistics ? String(statistics.poles) : "—" },
          { label: "Fastest laps", value: statistics ? String(statistics.fastestLaps) : "—" },
        ]}
        watermark={
          <DriverNumberMark
            {...(driver?.driverNumber != null && { number: driver.driverNumber })}
          />
        }
      />

      <Container className="flex flex-wrap items-end justify-between gap-4 py-8">
        <Select
          label="Driver"
          {...(driverId !== undefined && { value: driverId })}
          onValueChange={setSelectedDriverId}
          options={drivers.map((item) => ({
            value: item.id,
            label: item.abbreviation ? `${item.abbreviation} — ${item.fullName}` : item.fullName,
          }))}
          className="min-w-64"
        />
      </Container>

      <Section
        title="Race pace"
        description={
          teammate
            ? `Stint lap times vs. ${teammate.fullName} — lower is faster.`
            : "Stint lap times — lower is faster."
        }
      >
        {driverLapsQuery.isError || teammateLapsQuery.isError ? (
          <QueryError />
        ) : (
          <LineChart
            categories={pace.categories}
            series={[
              { name: driver?.abbreviation ?? "Driver", data: pace.driverData, ...primaryColor },
              ...(pace.teammateData && teammate
                ? [{ name: teammate.fullName, data: pace.teammateData, ...secondaryColor }]
                : []),
            ]}
            yAxisLabel="Lap time (s)"
            valueFormatter={(value) => `${value.toFixed(1)}s`}
            ariaLabel={`${driver?.fullName ?? "Driver"} race pace compared with teammate`}
            height={400}
          />
        )}
      </Section>

      <Section title="Season form" description="Qualifying pace and finishing position by round.">
        <div className="grid grid-cols-1 gap-x-16 gap-y-10 laptop:grid-cols-2">
          <div className="flex flex-col gap-4">
            <h3 className="font-mono text-caption uppercase tracking-wide text-text-muted">
              Qualifying vs. race
            </h3>
            {resultsError ? (
              <QueryError />
            ) : (
              <BarChart
                categories={qualifyingVsRaceRows.map((row) => `R${row.round}`)}
                series={[
                  {
                    name: "Qualifying",
                    data: qualifyingVsRaceRows.map((row) => row.grid),
                    ...secondaryColor,
                  },
                  {
                    name: "Race",
                    data: qualifyingVsRaceRows.map((row) => row.finish),
                    ...primaryColor,
                  },
                ]}
                yAxisLabel="Position"
                valueFormatter={(value) => `P${value}`}
                ariaLabel={`${driver?.fullName ?? "Driver"} qualifying versus race positions`}
              />
            )}
          </div>

          <div className="flex flex-col gap-4">
            <h3 className="font-mono text-caption uppercase tracking-wide text-text-muted">
              Position progression
            </h3>
            {resultsError ? (
              <QueryError />
            ) : (
              <LineChart
                categories={progressionRows.map((row) => `R${row.round}`)}
                series={[
                  {
                    name: driver?.abbreviation ?? "Driver",
                    data: progressionRows.map((row) => row.finish),
                    ...primaryColor,
                  },
                ]}
                yAxisLabel="Finish"
                yAxisInverse
                valueFormatter={(value) => `P${value}`}
                ariaLabel={`${driver?.fullName ?? "Driver"} finishing position progression`}
              />
            )}
          </div>
        </div>

        {resultsLoading ? (
          <p className="mt-6 font-mono text-caption uppercase tracking-wide text-text-muted">
            Syncing telemetry…
          </p>
        ) : null}

        <p className="mt-10 font-mono text-caption uppercase tracking-wide text-text-muted">
          Speed, throttle, and brake traces —{" "}
          <a
            href="/telemetry"
            className="text-constructor-primary transition-colors duration-(--duration-fast) ease-standard hover:text-accent-hover"
          >
            Telemetry Center
          </a>
        </p>
      </Section>
    </>
  );
}

/**
 * The driver's number as a giant, near-invisible background numeral
 * (docs' driver-dossier equivalent of Mission Control's circuit graphic) —
 * a placeholder for real driver photography/silhouettes once those assets
 * exist, per the redesign brief's media pipeline.
 */
function DriverNumberMark({ number }: { number?: number }) {
  if (number == null) return null;
  return (
    <span
      className="font-dotmatrix leading-none text-constructor-primary tabular-nums"
      style={{ fontSize: "min(32vw, 22rem)" }}
    >
      {number}
    </span>
  );
}
