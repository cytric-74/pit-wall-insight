import { createBrowserRouter } from "react-router";

import { NAV_ITEMS } from "../constants/navigation.js";
import { RootLayout } from "../layouts/RootLayout.js";
import { MissionControlPage } from "./MissionControlPage.js";
import { RouteholderPage } from "./RouteholderPage.js";

export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: NAV_ITEMS.map((item) =>
      item.href === "/"
        ? { index: true as const, element: <MissionControlPage /> }
        : { path: item.href, element: <RouteholderPage title={item.label} /> },
    ),
  },
]);
