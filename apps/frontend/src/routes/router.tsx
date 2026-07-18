import { createBrowserRouter } from "react-router";
import type { ReactElement } from "react";

import { NAV_ITEMS } from "../constants/navigation.js";
import { DriverDossierPage } from "../features/drivers/DriverDossierPage.js";
import { RootLayout } from "../layouts/RootLayout.js";
import { MissionControlPage } from "./MissionControlPage.js";
import { RouteholderPage } from "./RouteholderPage.js";

/** Routes with a real page; anything not listed falls back to a placeholder. */
const IMPLEMENTED_PAGES: Record<string, ReactElement> = {
  "/": <MissionControlPage />,
  "/drivers": <DriverDossierPage />,
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
