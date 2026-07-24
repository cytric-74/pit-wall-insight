/**
 * Structural components (docs/09_COMPONENT_LIBRARY.md).
 * Implemented: Container, Hero, Section, Stat, StatGroup, InstrumentGauge.
 * Not yet implemented: Sidebar, Navbar, Footer, ResizablePanel, SplitView
 * (Sidebar/Footer already exist as app-level components in
 * apps/frontend/src/layouts/).
 *
 * `Features`/`Statistics` (the static marketing-band components Mission
 * Control used to render below its Hero) were removed as part of the
 * editorial redesign — restating capability areas in prose duplicated the
 * persistent sidebar nav, and that register reads as a marketing page
 * rather than engineering software (docs/assets/14_DESIGN_PRINCIPLES.md
 * Principle II). Deleted rather than kept unused.
 *
 * `Dashboard`/`WidgetGrid` (from `./Dashboard.js`) and `Widget` (from
 * `../cards/Widget.js`) are deprecated as of the editorial redesign — see
 * their own file-level comments. `Section`/`Stat`/`StatGroup`/
 * `InstrumentGauge` are the primitives every page composes from going
 * forward; `Dashboard`/`WidgetGrid`/`Widget` are re-exported only until
 * the last page still using them (Settings) migrates, at which point they
 * get deleted rather than kept as a permanent second option.
 */

export * from "./Container.js";
export * from "./Hero.js";
export * from "./InstrumentGauge.js";
export * from "./Section.js";
export * from "./Stat.js";
