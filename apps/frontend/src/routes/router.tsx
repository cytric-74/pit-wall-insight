import { lazy } from "react";
import { createBrowserRouter } from "react-router";
import type { ReactElement } from "react";

import { NAV_ITEMS } from "../constants/navigation.js";
import { RootLayout } from "../layouts/RootLayout.js";
import { RouteholderPage } from "./RouteholderPage.js";

const MissionControlPage = lazy(() =>
  import("../features/dashboard/MissionControlPage.js").then((m) => ({
    default: m.MissionControlPage,
  })),
);
const DriverDossierPage = lazy(() =>
  import("../features/drivers/DriverDossierPage.js").then((m) => ({
    default: m.DriverDossierPage,
  })),
);
const ConstructorIntelligencePage = lazy(() =>
  import("../features/constructors/ConstructorIntelligencePage.js").then((m) => ({
    default: m.ConstructorIntelligencePage,
  })),
);
const RacePlaybackPage = lazy(() =>
  import("../features/races/RacePlaybackPage.js").then((m) => ({ default: m.RacePlaybackPage })),
);
const CircuitExplorerPage = lazy(() =>
  import("../features/circuits/CircuitExplorerPage.js").then((m) => ({
    default: m.CircuitExplorerPage,
  })),
);
const TelemetryViewerPage = lazy(() =>
  import("../features/telemetry/TelemetryViewerPage.js").then((m) => ({
    default: m.TelemetryViewerPage,
  })),
);
const StrategyLabPage = lazy(() =>
  import("../features/strategy/StrategyLabPage.js").then((m) => ({ default: m.StrategyLabPage })),
);
const SeasonExplorerPage = lazy(() =>
  import("../features/season/SeasonExplorerPage.js").then((m) => ({
    default: m.SeasonExplorerPage,
  })),
);
const SettingsPage = lazy(() =>
  import("../features/settings/SettingsPage.js").then((m) => ({ default: m.SettingsPage })),
);

/** Routes with a real page; anything not listed falls back to a placeholder.
 *
 * Every entry is `React.lazy(() => import(...))` rather than a static
 * import — previously every page (and every page's ECharts usage) shipped
 * in one >1.2MB chunk regardless of which single route a visitor loaded
 * (Phase 7 audit, High). `RootLayout` wraps `<Outlet/>` in a `<Suspense>`
 * boundary that covers whichever of these renders.
 */
const IMPLEMENTED_PAGES: Record<string, ReactElement> = {
  "/": <MissionControlPage />,
  "/drivers": <DriverDossierPage />,
  "/constructors": <ConstructorIntelligencePage />,
  "/races": <RacePlaybackPage />,
  "/circuits": <CircuitExplorerPage />,
  "/telemetry": <TelemetryViewerPage />,
  "/strategy": <StrategyLabPage />,
  "/season": <SeasonExplorerPage />,
  "/settings": <SettingsPage />,
};

export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: NAV_ITEMS.map((item) => {
      const element = IMPLEMENTED_PAGES[item.href] ?? <RouteholderPage title={item.label} />;
      return item.href === "/" ? { index: true as const, element } : { path: item.href, element };
    }),
  },
]);
