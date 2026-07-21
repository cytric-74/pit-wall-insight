import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { forwardRef } from "react";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "../lib/cn.js";
import { Spinner } from "../loading/Spinner.js";

/**
 * Button variants (docs/assets/09_COMPONENT_STYLING.md — "Buttons"):
 * primary (constructor accent, one per section), secondary (neutral,
 * never competes), ghost (no background, border only when necessary),
 * danger (destructive actions). Every variant supports every state
 * (default/hover/pressed/loading/disabled).
 */
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md font-body text-body-sm font-medium transition-colors duration-(--duration-fast) ease-standard disabled:pointer-events-none disabled:opacity-40 [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        primary:
          "bg-constructor-primary text-text-inverse hover:bg-accent-hover active:bg-accent-active",
        secondary:
          "border border-border-default bg-surface-elevated text-text-primary hover:bg-surface-hover active:bg-surface-active",
        ghost: "bg-transparent text-text-primary hover:bg-surface-hover active:bg-surface-active",
        danger: "bg-danger text-text-inverse hover:brightness-110 active:brightness-95",
      },
      size: {
        sm: "h-9 px-3 text-label-md",
        md: "h-11 px-4",
        lg: "h-12 px-6 text-body-md",
        icon: "size-11 p-0",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  },
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  /** Render as the single child element (e.g. a router Link) instead of a <button>. */
  asChild?: boolean;
  /** Shows an inline Spinner and marks the button busy/disabled. Ignored when `asChild`. */
  isLoading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    { className, variant, size, asChild = false, isLoading = false, disabled, children, ...props },
    ref,
  ) => {
    if (asChild) {
      return (
        <Slot
          ref={ref}
          className={cn(buttonVariants({ variant, size, className }))}
          aria-busy={isLoading || undefined}
          data-cursor="button"
          {...props}
        >
          {children}
        </Slot>
      );
    }

    return (
      <button
        ref={ref}
        type={props.type ?? "button"}
        className={cn(buttonVariants({ variant, size, className }))}
        disabled={disabled || isLoading}
        aria-busy={isLoading || undefined}
        data-cursor="button"
        {...props}
      >
        {isLoading ? <Spinner className="size-4" aria-hidden="true" /> : null}
        {children}
      </button>
    );
  },
);
Button.displayName = "Button";

export { buttonVariants };
