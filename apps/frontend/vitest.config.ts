import { defineConfig } from "vitest/config";

/**
 * Separate from `vite.config.ts` on purpose — these are plain unit tests
 * over `.ts` utilities and the API client (no component rendering), so
 * they need neither the React plugin nor a DOM environment; keeping this
 * config standalone means running `vitest` never risks pulling the app's
 * build-time config (Tailwind plugin, `envDir`) into the test run.
 */
export default defineConfig({
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
    // `api-client.ts` reads `import.meta.env.VITE_API_URL` at module load
    // time; this config never loads the monorepo's real `.env` (see the
    // note above), so it's set explicitly here instead — a real value is
    // never actually requested since `fetch` itself is mocked in every test.
    env: {
      VITE_API_URL: "http://localhost:8000/api/v1",
    },
  },
});
