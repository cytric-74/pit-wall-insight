import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@pit-wall-insight/ui";
import { Search } from "lucide-react";

export interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

/**
 * Placeholder only (per task scope): the palette opens, is fully keyboard
 * accessible, and follows the documented open sequence
 * (docs/10_ANIMATION_AND_INTERACTIONS.md — "Command Palette": background
 * fade -> palette -> cursor focus) via the shared Dialog primitive, but
 * has no command registry or search behavior wired up yet.
 *
 * The search input is disabled rather than live — an enabled text field
 * that visibly accepts typing but silently does nothing on every
 * keystroke reads as broken, not unfinished (Phase 7 audit, Low/Bug).
 * Re-enable once it's actually wired to the Search API.
 */
export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="top-24 max-w-xl translate-y-0 gap-0 p-0">
        <DialogTitle className="sr-only">Command palette</DialogTitle>
        <DialogDescription className="sr-only">
          Search for a page or action. No commands are wired up yet.
        </DialogDescription>
        <div className="flex items-center gap-3 border-b border-border-default px-4">
          <Search className="size-4 shrink-0 text-text-muted" aria-hidden="true" />
          <input
            type="text"
            disabled
            aria-label="Command palette search"
            placeholder="Command search isn't available yet"
            className="h-14 w-full bg-transparent font-mono text-body-sm text-text-primary placeholder:text-text-disabled focus:outline-none disabled:cursor-not-allowed"
          />
        </div>
        <p className="p-6 text-center text-body-sm text-text-muted">No commands available yet.</p>
      </DialogContent>
    </Dialog>
  );
}
