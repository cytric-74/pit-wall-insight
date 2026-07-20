/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base URL of the Pit Wall Insight API, e.g. `http://localhost:8000/api/v1`. */
  readonly VITE_API_URL: string;
  readonly VITE_APP_NAME: string;
  readonly VITE_ENVIRONMENT: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
