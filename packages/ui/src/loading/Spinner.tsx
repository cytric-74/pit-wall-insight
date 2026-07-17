import { LoaderCircle } from "lucide-react";
import type { SVGAttributes } from "react";

import { cn } from "../lib/cn.js";

export type SpinnerProps = SVGAttributes<SVGSVGElement>;

/**
 * Reserved for small, inline loading contexts (inside a Button, an inline
 * refresh action) — docs/assets/09_COMPONENT_STYLING.md explicitly prefers
 * Skeletons for content loading over spinners; this exists for the cases
 * where a skeleton doesn't apply.
 */
export function Spinner({ className, ...props }: SpinnerProps) {
  return (
    <LoaderCircle
      role="status"
      aria-label="Loading"
      className={cn("animate-spin text-current motion-reduce:animate-none", className)}
      {...props}
    />
  );
}
