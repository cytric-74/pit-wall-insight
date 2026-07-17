// Shared ESLint flat config consumed by every package in the monorepo.
// Individual packages extend this with a two-line `eslint.config.mjs`:
//
//   import base from "@pit-wall-insight/config/eslint/base.mjs";
//   export default base;

import js from "@eslint/js";
import tseslint from "typescript-eslint";
import eslintConfigPrettier from "eslint-config-prettier";

export default tseslint.config(
  {
    ignores: ["**/dist/**", "**/build/**", "**/.turbo/**", "**/node_modules/**", "**/coverage/**"],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  eslintConfigPrettier,
);
