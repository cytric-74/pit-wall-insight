import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merges class names, resolving conflicting Tailwind utility classes
 * (e.g. `cn("p-2", condition && "p-4")` keeps only `p-4`).
 *
 * Every component in this library builds its `className` through `cn()`
 * rather than string concatenation, per docs/09_COMPONENT_LIBRARY.md's
 * "Props Standards" (every component accepts and merges `className`).
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
