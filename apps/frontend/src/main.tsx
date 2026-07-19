import { TooltipProvider } from "@pit-wall-insight/ui";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router";

import { router } from "./routes/router.js";
import "./styles/globals.css";
import { PreferencesProvider, ThemeProvider } from "./themes/index.js";

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("Root element #root not found.");
}

createRoot(rootElement).render(
  <StrictMode>
    <PreferencesProvider>
      <ThemeProvider>
        <TooltipProvider>
          <RouterProvider router={router} />
        </TooltipProvider>
      </ThemeProvider>
    </PreferencesProvider>
  </StrictMode>,
);
