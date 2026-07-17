import * as TabsPrimitive from "@radix-ui/react-tabs";

import { cn } from "../lib/cn.js";

/**
 * "Tabs divide context. Not content. Only one active tab should exist.
 * Active state uses constructor accent." (docs/assets/09_COMPONENT_STYLING.md)
 *
 * Built on Radix Tabs for correct roving-tabindex keyboard navigation
 * (arrow keys between tabs, Home/End) and tablist/tab/tabpanel ARIA roles.
 */
export const Tabs = TabsPrimitive.Root;

export function TabsList({ className, ...props }: TabsPrimitive.TabsListProps) {
  return (
    <TabsPrimitive.List
      className={cn("inline-flex items-center gap-1 border-b border-border-default", className)}
      {...props}
    />
  );
}

export function TabsTrigger({ className, ...props }: TabsPrimitive.TabsTriggerProps) {
  return (
    <TabsPrimitive.Trigger
      className={cn(
        "border-b-2 border-transparent px-3 py-2 font-body text-body-sm text-text-secondary transition-colors duration-(--duration-fast) ease-standard hover:text-text-primary data-[state=active]:border-constructor-primary data-[state=active]:text-text-primary disabled:pointer-events-none disabled:opacity-40",
        className,
      )}
      {...props}
    />
  );
}

export function TabsContent({ className, ...props }: TabsPrimitive.TabsContentProps) {
  return (
    <TabsPrimitive.Content
      className={cn("pt-4 focus-visible:outline-none", className)}
      {...props}
    />
  );
}
