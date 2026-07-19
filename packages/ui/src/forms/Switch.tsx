import { forwardRef, useId } from "react";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "../lib/cn.js";

export interface SwitchProps extends Omit<
  ButtonHTMLAttributes<HTMLButtonElement>,
  "onChange" | "value" | "type"
> {
  label: string;
  /** Keeps the label programmatically associated but visually hidden. */
  hideLabel?: boolean;
  description?: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
}

/**
 * Boolean control (docs/09_COMPONENT_LIBRARY.md lists "Switch" among the
 * foundation components). A plain `role="switch"` button rather than a
 * Radix primitive — unlike Select/Dialog/Tabs/Tooltip, a toggle has no
 * listbox, focus-trap, or roving-tabindex behavior to delegate; native
 * button semantics plus `aria-checked` cover it fully.
 */
export const Switch = forwardRef<HTMLButtonElement, SwitchProps>(
  (
    {
      label,
      hideLabel = false,
      description,
      checked,
      onCheckedChange,
      disabled,
      className,
      id,
      ...props
    },
    ref,
  ) => {
    const generatedId = useId();
    const switchId = id ?? generatedId;
    const descriptionId = description ? `${switchId}-description` : undefined;

    return (
      <div className="flex items-center justify-between gap-4">
        <div className="flex flex-col gap-0.5">
          <label
            htmlFor={switchId}
            className={cn("text-body-sm text-text-primary", hideLabel && "sr-only")}
          >
            {label}
          </label>
          {description ? (
            <p id={descriptionId} className="text-caption text-text-muted">
              {description}
            </p>
          ) : null}
        </div>
        <button
          ref={ref}
          id={switchId}
          type="button"
          role="switch"
          aria-checked={checked}
          {...(descriptionId ? { "aria-describedby": descriptionId } : {})}
          disabled={disabled}
          onClick={() => onCheckedChange(!checked)}
          className={cn(
            "relative inline-flex h-6 w-11 shrink-0 items-center rounded-full border border-border-default transition-colors duration-(--duration-fast) ease-standard disabled:pointer-events-none disabled:opacity-40",
            checked ? "bg-constructor-primary" : "bg-surface-elevated",
            className,
          )}
          {...props}
        >
          <span
            aria-hidden="true"
            className={cn(
              "inline-block size-4 translate-x-1 rounded-full bg-text-primary transition-transform duration-(--duration-fast) ease-standard",
              checked && "translate-x-6",
            )}
          />
        </button>
      </div>
    );
  },
);
Switch.displayName = "Switch";
