import Lenis from "lenis";
import { useEffect } from "react";

function prefersReducedMotion(): boolean {
  return (
    document.documentElement.getAttribute("data-motion") === "reduced" ||
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}

/**
 * Velocity-based smooth scroll (docs/03_DESIGN_SYSTEM.md / docs/assets/04_LAYOUT_SYSTEM.md
 * — "Scroll: Powered by Lenis. Smooth interpolation, momentum, scroll
 * restoration."). Mounted once at the root layout, never per-page.
 *
 * Skipped entirely under reduced motion (both the OS signal and the
 * in-app override, `data-motion="reduced"` set by `PreferencesProvider`)
 * rather than running with reduced settings — docs/assets/05_MOTION_SYSTEM.md
 * "Reduced Motion" calls for native, unmodified scroll behavior, and Lenis's
 * momentum/easing is exactly the kind of movement that section is about.
 *
 * Reacts live to both signals (a `data-motion` attribute change from the
 * Settings toggle, or the OS setting changing mid-session) by tearing down
 * or (re)creating the Lenis instance, rather than only checking once at
 * mount — the Settings page's "Reduce motion" switch would otherwise
 * require a full reload to take effect on scroll behavior specifically.
 */
export function useSmoothScroll(): void {
  useEffect(() => {
    let lenis: Lenis | undefined;
    let frame: number | undefined;

    function start() {
      if (lenis) return;
      lenis = new Lenis({
        duration: 1.1,
        easing: (t: number) => 1 - Math.pow(1 - t, 3),
        smoothWheel: true,
      });
      const raf = (time: number) => {
        lenis?.raf(time);
        frame = requestAnimationFrame(raf);
      };
      frame = requestAnimationFrame(raf);
    }

    function stop() {
      if (frame !== undefined) cancelAnimationFrame(frame);
      lenis?.destroy();
      lenis = undefined;
      frame = undefined;
    }

    function sync() {
      if (prefersReducedMotion()) stop();
      else start();
    }

    sync();

    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    media.addEventListener("change", sync);
    const observer = new MutationObserver(sync);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-motion"],
    });

    return () => {
      media.removeEventListener("change", sync);
      observer.disconnect();
      stop();
    };
  }, []);
}
