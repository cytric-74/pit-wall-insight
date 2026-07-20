import {
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

import { resolveConstructorId } from "../../lib/constructor-id.js";
import { useCurrentSeasonRaces } from "../races/queries.js";
import { useSessionResultsForRaces } from "../sessions/queries.js";
import {
  useDriver,
  useDriverLaps,
  useDrivers,
  useDriverStatistics,
  useTeammate,
} from "./queries.js";
import { buildPaceSeries, extractRoundPositions } from "./utils.js";

const RACE_SESSION_TYPE = "R";

/**
 * Driver Dossier (docs/assets/04_LAYOUT_SYSTEM.md — "Driver Dossier
 * Layout": Driver Overview -> Performance Summary -> Lap Analysis ->
 * Telemetry -> Race History -> Comparisons). Backed by `/api/v1/drivers/*`
 * (docs/08_API_SPECIFICATION.md — "Drivers"); "Telemetry" stays a
 * permanent `loading` placeholder — no telemetry data exists in this
 * pipeline (see docs/06_DATA_ENGINEERING.md scope).
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
  const qualifyingVsRaceRows = positions.filter((row) => row.grid !== null && row.finish !== null);
  const progressionRows = positions.filter((row) => row.finish !== null);

  return (
    <>
      <Hero
        eyebrow="Driver Dossier"
        title={driver?.fullName ?? "Loading driver…"}
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
      />

      <Container className="flex flex-col gap-8 pb-(--section-gap)">
        <div className="flex flex-wrap items-end justify-between gap-4">
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
        </div>

        <WidgetGrid>
          <Widget
            title="Race pace"
            description={
              teammate
                ? `Stint lap times vs. ${teammate.fullName} — lower is faster.`
                : "Stint lap times — lower is faster."
            }
            loading={
              driverLapsQuery.isPending || (teammate !== undefined && teammateLapsQuery.isPending)
            }
            className="sm:col-span-2 laptop:col-span-12"
          >
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
            />
          </Widget>

          <Widget
            title="Qualifying vs. race"
            description="Grid position against finishing position by round — lower is better."
            loading={resultsLoading}
            className="laptop:col-span-6"
          >
            <BarChart
              categories={qualifyingVsRaceRows.map((row) => `R${row.round}`)}
              series={[
                {
                  name: "Qualifying",
                  data: qualifyingVsRaceRows.map((row) => row.grid!),
                  ...secondaryColor,
                },
                {
                  name: "Race",
                  data: qualifyingVsRaceRows.map((row) => row.finish!),
                  ...primaryColor,
                },
              ]}
              yAxisLabel="Position"
              valueFormatter={(value) => `P${value}`}
              ariaLabel={`${driver?.fullName ?? "Driver"} qualifying versus race positions`}
            />
          </Widget>

          <Widget
            title="Position progression"
            description="Finishing position across the season — lower is better."
            loading={resultsLoading}
            className="laptop:col-span-6"
          >
            <LineChart
              categories={progressionRows.map((row) => `R${row.round}`)}
              series={[
                {
                  name: driver?.abbreviation ?? "Driver",
                  data: progressionRows.map((row) => row.finish!),
                  ...primaryColor,
                },
              ]}
              yAxisLabel="Finish"
              yAxisInverse
              valueFormatter={(value) => `P${value}`}
              ariaLabel={`${driver?.fullName ?? "Driver"} finishing position progression`}
            />
          </Widget>

          <Widget
            title="Telemetry"
            description="Speed, throttle, and brake traces"
            href="/telemetry"
            linkLabel="Telemetry Center"
            loading
            className="sm:col-span-2 laptop:col-span-12"
          />
        </WidgetGrid>
      </Container>
    </>
  );
}
