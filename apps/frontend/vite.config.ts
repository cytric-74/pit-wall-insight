import path from "node:path";
import { fileURLToPath } from "node:url";

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Every app in this monorepo reads configuration from one root `.env`
  // (see apps/backend/app/core/config.py / apps/ingestion/config/settings.py
  // for the same convention) — Vite otherwise only looks in this package's
  // own directory.
  envDir: path.resolve(dirname, "../.."),
});
