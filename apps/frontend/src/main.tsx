import { TooltipProvider } from "@pit-wall-insight/ui";
import { QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router";

import { ErrorBoundary } from "./lib/error-boundary.js";
import { queryClient } from "./lib/query-client.js";
import { router } from "./routes/router.js";
import "./styles/globals.css";
import { PreferencesProvider, ThemeProvider } from "./themes/index.js";

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("Root element #root not found.");
}

// `api-client.ts` reads `import.meta.env.VITE_API_URL` with only a
// compile-time `string` type and no runtime check — left unset, the
// failure previously surfaced only at first request time, deep inside a
// query, as a confusing `URL` constructor error far from the actual
// misconfiguration (Phase 7 audit, Medium).
if (!import.meta.env.VITE_API_URL) {
  throw new Error(
    "VITE_API_URL is not set. Copy .env.example to .env and set VITE_API_URL to the backend's base URL.",
  );
}

createRoot(rootElement).render(
  <StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <PreferencesProvider>
          <ThemeProvider>
            <TooltipProvider>
              <RouterProvider router={router} />
            </TooltipProvider>
          </ThemeProvider>
        </PreferencesProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  </StrictMode>,
);
