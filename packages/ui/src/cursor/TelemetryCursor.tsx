import { motion, useMotionValue, useReducedMotion, useSpring } from "framer-motion";
import { useEffect, useState } from "react";

export type CursorVariant = "default" | "button" | "chart" | "drag";

const RING_SCALE: Record<CursorVariant, number> = {
  default: 1,
  button: 2.75,
  chart: 1,
  drag: 3.5,
};

/**
 * The Telemetry Probe (docs/assets/07_CURSOR_SYSTEM.md). An instrument, not
 * a gimmick: a small, perfectly round core dot that follows the pointer
 * with slight mechanical damping, gaining a thin interaction ring near
 * buttons/links and switching to a crosshair over charts.
 *
 * Interactive elements opt in with `data-cursor="button" | "chart" | "drag"`
 * on themselves or an ancestor — nothing is wired centrally per-component,
 * so this can be adopted incrementally page by page. Elements with no
 * `data-cursor` ancestor get the default minimal dot.
 *
 * Disabled entirely (renders nothing, native cursor stays untouched) when:
 * - the pointer is not fine (touch/coarse devices — desktop only per docs)
 * - reduced motion is active (OS signal or the in-app override)
 * Text inputs, textareas, and contenteditable regions always keep the
 * native I-beam/native cursor (docs: "Text Selection... Never replace it",
 * "Input Fields: use native text cursor") — handled by CSS in globals.css
 * rather than JS state, since it must apply unconditionally.
 */
export function TelemetryCursor(): React.JSX.Element | null {
  const prefersReducedMotion = useReducedMotion();
  const [enabled, setEnabled] = useState(false);
  const [variant, setVariant] = useState<CursorVariant>("default");
  const [visible, setVisible] = useState(false);

  const x = useMotionValue(-100);
  const y = useMotionValue(-100);
  const springX = useSpring(x, { damping: 34, stiffness: 500, mass: 0.4 });
  const springY = useSpring(y, { damping: 34, stiffness: 500, mass: 0.4 });

  useEffect(() => {
    const canHover = window.matchMedia("(pointer: fine)").matches;
    setEnabled(canHover && !prefersReducedMotion);
  }, [prefersReducedMotion]);

  useEffect(() => {
    if (!enabled) return;

    document.documentElement.classList.add("pw-cursor-active");

    function handleMove(event: PointerEvent) {
      x.set(event.clientX);
      y.set(event.clientY);
      setVisible(true);
      const target =
        event.target instanceof Element ? event.target.closest<HTMLElement>("[data-cursor]") : null;
      setVariant((target?.dataset.cursor as CursorVariant | undefined) ?? "default");
    }

    function handleLeave() {
      setVisible(false);
    }

    window.addEventListener("pointermove", handleMove);
    document.documentElement.addEventListener("pointerleave", handleLeave);
    return () => {
      document.documentElement.classList.remove("pw-cursor-active");
      window.removeEventListener("pointermove", handleMove);
      document.documentElement.removeEventListener("pointerleave", handleLeave);
    };
  }, [enabled, x, y]);

  if (!enabled) return null;

  return (
    <motion.div
      aria-hidden="true"
      className="pointer-events-none fixed left-0 top-0 z-(--z-toast)"
      style={{ x: springX, y: springY, opacity: visible ? 1 : 0 }}
      transition={{ opacity: { duration: 0.15 } }}
    >
      {/* Core dot — "perfectly round, minimal, no glow, no shadow" */}
      <div
        className="absolute rounded-full bg-constructor-cursor"
        style={{
          width: "var(--cursor-size)",
          height: "var(--cursor-size)",
          transform: "translate(-50%, -50%)",
        }}
      />
      {/* Interaction ring — only visible for button/drag variants */}
      <motion.div
        className="absolute rounded-full border border-constructor-cursor"
        animate={{
          scale: RING_SCALE[variant],
          opacity: variant === "button" || variant === "drag" ? 1 : 0,
        }}
        transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
        style={{
          width: "var(--cursor-size)",
          height: "var(--cursor-size)",
          transform: "translate(-50%, -50%)",
        }}
      />
      {/* Engineering crosshair — chart variant only */}
      {variant === "chart" ? (
        <>
          <div
            className="absolute bg-constructor-cursor/60"
            style={{
              width: "var(--cursor-ring)",
              height: "var(--cursor-crosshair)",
              transform: "translate(-50%, -50%)",
            }}
          />
          <div
            className="absolute bg-constructor-cursor/60"
            style={{
              width: "var(--cursor-crosshair)",
              height: "var(--cursor-ring)",
              transform: "translate(-50%, -50%)",
            }}
          />
        </>
      ) : null}
    </motion.div>
  );
}
