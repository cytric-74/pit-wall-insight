import { CircleAlert } from "lucide-react";

/**
 * The widget-level "this query failed" state. Every migrated page wired
 * `loading` to a query's `isPending` but never checked `isError` — on a
 * failed fetch the widget just fell through to its empty-data branch,
 * showing "Loading…"/nothing forever with no indication anything went
 * wrong (Phase 7 audit, Critical). Reuses the exact error-text pattern
 * already established for form fields (`packages/ui/src/forms/Select.tsx`)
 * rather than introducing a new visual language for errors.
 */
export function QueryError({
  message = "Something went wrong loading this data.",
}: {
  message?: string;
}) {
  return (
    <p role="alert" className="flex items-center gap-1 text-caption text-danger">
      <CircleAlert className="size-3.5 shrink-0" aria-hidden="true" />
      {message}
    </p>
  );
}
