import { CircleAlert } from "lucide-react";
import { forwardRef, useId } from "react";
import type { TextareaHTMLAttributes } from "react";

import { cn } from "../lib/cn.js";

export interface TextareaProps extends Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, "id"> {
  label: string;
  description?: string;
  error?: string;
  id?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, description, error, id, required, rows = 4, ...props }, ref) => {
    const generatedId = useId();
    const textareaId = id ?? generatedId;
    const descriptionId = description ? `${textareaId}-description` : undefined;
    const errorId = error ? `${textareaId}-error` : undefined;
    const describedBy = [descriptionId, errorId].filter(Boolean).join(" ") || undefined;

    return (
      <div className="flex flex-col gap-2">
        <label
          htmlFor={textareaId}
          className="text-label-md font-medium uppercase tracking-wide text-text-secondary"
        >
          {label}
          {required ? <span className="text-danger"> *</span> : null}
        </label>
        <textarea
          ref={ref}
          id={textareaId}
          rows={rows}
          required={required}
          aria-invalid={Boolean(error) || undefined}
          aria-describedby={describedBy}
          className={cn(
            "resize-y rounded-sm border bg-surface-primary px-4 py-3 font-mono text-body-sm text-text-primary transition-colors duration-(--duration-fast) ease-standard placeholder:text-text-disabled disabled:cursor-not-allowed disabled:opacity-40",
            error
              ? "border-danger"
              : "border-border-default hover:border-border-hover focus:border-border-focus",
            className,
          )}
          {...props}
        />
        {description ? (
          <p id={descriptionId} className="text-caption text-text-muted">
            {description}
          </p>
        ) : null}
        {error ? (
          <p id={errorId} role="alert" className="flex items-center gap-1 text-caption text-danger">
            <CircleAlert className="size-3.5 shrink-0" aria-hidden="true" />
            {error}
          </p>
        ) : null}
      </div>
    );
  },
);
Textarea.displayName = "Textarea";
