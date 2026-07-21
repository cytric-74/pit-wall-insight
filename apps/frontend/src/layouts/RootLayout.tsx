import { cn, Spinner, TelemetryCursor } from "@pit-wall-insight/ui";
import { Suspense, useEffect, useState } from "react";
import { Outlet } from "react-router";

import { useSmoothScroll } from "../lib/smooth-scroll.js";
import { CommandPalette } from "./CommandPalette.js";
import { Footer } from "./Footer.js";
import { Header } from "./Header.js";
import { Sidebar } from "./Sidebar.js";

/**
 * Persistent chrome: Sidebar + Header + <Outlet/> + Footer
 * (docs/assets/04_LAYOUT_SYSTEM.md — "Interface Rhythm": Header -> Hero ->
 * Primary Analytics -> Secondary Analytics -> Supporting Panels -> Footer;
 * the Hero/Analytics portion is whatever the current route renders).
 * No dashboard content lives here — only the shell around it.
 *
 * Mounts the two app-wide "systems" exactly once here, never per-page:
 * the Telemetry Probe cursor (docs/assets/07_CURSOR_SYSTEM.md) and Lenis
 * smooth scroll (docs/assets/04_LAYOUT_SYSTEM.md — "Scroll").
 */
export function RootLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  useSmoothScroll();

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setCommandPaletteOpen((open) => !open);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="min-h-screen bg-background-primary text-text-primary">
      <Sidebar collapsed={collapsed} onToggleCollapsed={() => setCollapsed((value) => !value)} />

      <div
        className={cn(
          "flex min-h-screen flex-col ml-(--sidebar-collapsed) transition-[margin] duration-(--duration-panel) ease-standard",
          !collapsed && "laptop:ml-(--sidebar-width)",
        )}
      >
        <Header onOpenCommandPalette={() => setCommandPaletteOpen(true)} />
        <main className="flex-1 px-6 py-8">
          <Suspense
            fallback={
              <div className="flex justify-center py-16">
                <Spinner className="size-8" aria-label="Loading page…" />
              </div>
            }
          >
            <Outlet />
          </Suspense>
        </main>
        <Footer />
      </div>

      <CommandPalette open={commandPaletteOpen} onOpenChange={setCommandPaletteOpen} />
      <TelemetryCursor />
    </div>
  );
}
