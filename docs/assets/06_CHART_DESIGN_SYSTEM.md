# CHART DESIGN SYSTEM

# Pit Wall Insight

Version: 1.0

Status: Living Document

---

# Purpose

Charts are the heart of Pit Wall Insight.

The interface exists to help users understand data.

Charts are not external components.

Charts are first-class citizens.

Every visualization should feel like it belongs inside a Formula One race engineering workstation.

---

# Chart Philosophy

Charts should never feel like dashboard widgets.

They should feel like engineering instruments.

Every chart should answer a question.

If a visualization cannot answer a question,

it should not exist.

---

# Telemetry Instrument Design

Pit Wall Insight does not display graphs.

It displays telemetry instruments.

Each visualization behaves as though it belongs to the same operating system.

Every graph follows

• Typography System

• Motion System

• Color System

• Cursor System

• Theme Engine

No visualization should introduce its own design language.

---

# Chart DNA

Every visualization should communicate

Precision

↓

Clarity

↓

Confidence

↓

Engineering

↓

Performance

↓

Insight

---

# Design Goals

Users should instantly understand

• What happened

• Why it happened

• What changed

• What should be compared

---

# Visual Style

Charts should feel

Minimal

Mechanical

Technical

Quiet

Premium

Readable

Never

Colorful

Playful

Corporate

Noisy

Decorative

---

# Information Hierarchy

Chart Title

↓

Primary Data

↓

Comparison

↓

Annotations

↓

Grid

↓

Metadata

Nothing should compete with the data itself.

---

# Chart Layout

Every chart contains

Header

↓

Visualization

↓

Legend

↓

Metadata

↓

Actions

Always maintain this structure.

---

# Titles

Large

Bold

Minimal

Example

Race Pace Evolution

Tyre Degradation

Sector Comparison

Strategy Timeline

Never

Average Graph

Chart 1

Interesting Statistics

---

# Labels

Always concise.

Examples

SPEED

RPM

TYRE LIFE

SECTOR

POSITION

LAP

FUEL

Never write long labels.

---

# Typography

Chart Title

Space Grotesk

Axis

IBM Plex Mono

Tooltip

IBM Plex Mono

Legend

Inter

Metadata

IBM Plex Mono

---

# Grid Philosophy

Gridlines should guide.

Never dominate.

Very subtle.

Very thin.

Very low opacity.

Engineering inspired.

---

# Axis

Axis should remain neutral.

Never colorful.

Never thick.

Always secondary.

---

# Tick Marks

Tick marks should resemble measurement tools.

Small.

Consistent.

Mechanical.

---

# Data Lines

Primary line

Slightly thicker.

Comparison line

Slightly thinner.

Reference line

Dashed.

Prediction

Dotted.

Historical

Reduced opacity.

---

# Curves

Avoid exaggerated smoothing.

Respect the data.

Accuracy over aesthetics.

---

# Data Points

Hidden by default.

Appear only

on interaction

or

important events.

Avoid visual clutter.

---

# Hover States

Hover should activate

Crosshair

↓

Tooltip

↓

Point Highlight

↓

Related KPI

↓

Axis Highlight

Everything should feel connected.

---

# Tooltips

Dark background.

Thin border.

Constructor accent.

Minimal information.

Fast appearance.

Never oversized.

Never rounded excessively.

---

# Legends

Legends should remain understated.

Positioned consistently.

Never dominate the chart.

---

# Animations

Every chart loads in the same order.

Grid

↓

Axis

↓

Labels

↓

Data

↓

Interactions

Never animate everything simultaneously.

---

# Empty States

Examples

NO DATA AVAILABLE

NO TELEMETRY FOUND

SESSION NOT SELECTED

No illustrations.

No emojis.

---

# Loading States

Display telemetry initialization.

INITIALIZING

↓

FETCHING DATA

↓

CALCULATING

↓

READY

Avoid traditional loading spinners.

---

# Constructor Themes

Every constructor changes

Primary Line

Secondary Line

Hover Accent

Tooltip Accent

Crosshair

Selection

Hero Visualization

Grid remains unchanged.

Axis remains unchanged.

Layout remains unchanged.

---

# Ferrari

Aggressive

Warm

Confident

Sharper highlights

---

# Mercedes

Clean

Cool

Technical

Controlled

---

# McLaren

Dynamic

Energetic

Fast

Bright highlights

---

# Aston Martin

Luxury

Elegant

Mechanical

Subtle glow

---

# Williams

Minimal

Professional

Balanced

Engineering blue

---

# Red Bull

Confident

High contrast

Strong emphasis

---

# Multi-Series Charts

Never exceed visual clarity.

Differentiate using

Color

↓

Line Style

↓

Opacity

↓

Thickness

Avoid rainbow palettes.

---

# Bar Charts

Sharp corners.

Minimal radius.

Consistent spacing.

No gradients.

Hover brightens only.

---

# Line Charts

The signature visualization.

Should resemble telemetry traces.

Smooth.

Accurate.

Precise.

---

# Area Charts

Use sparingly.

Only when emphasizing magnitude.

Opacity remains low.

---

# Scatter Charts

Small markers.

Engineering precision.

Never oversized circles.

---

# Heatmaps

Dark background.

Constructor accent.

Smooth transitions.

Readable values.

---

# Radar Charts

Minimal grid.

Thin lines.

Rarely used.

Only when comparison benefits.

---

# Pie Charts

Avoid whenever possible.

Prefer bars.

Only use when proportions are the primary insight.

---

# Tables

Tables complement charts.

Never replace them.

Maintain identical typography.

---

# KPI Integration

Hovering a chart may update

KPIs

↓

Cards

↓

Statistics

↓

Related Panels

The interface behaves like one connected system.

---

# Telemetry Mode

Telemetry charts should include

Crosshair

↓

Live Coordinate

↓

Measurement Labels

↓

Cursor Probe

↓

Engineering Scale

Users should feel like they are inspecting instruments.

---

# Cursor Integration

Normal

Telemetry Probe

Chart Hover

Engineering Crosshair

Drag

Measurement Cursor

Selection

Precision Indicator

Never use default browser cursor over charts.

---

# Zoom

Smooth.

Predictable.

Maintain orientation.

Never lose context.

---

# Pan

Only when beneficial.

Motion remains dampened.

No sudden jumps.

---

# Filtering

Transitions should preserve continuity.

Users should never lose their mental model.

---

# Comparison Mode

Primary dataset

Constructor Accent

Secondary

Neutral White

Historical

Muted Gray

Prediction

Purple

Semantic colors always override constructor colors.

---

# Annotation System

Annotations should remain subtle.

Examples

Safety Car

Pit Stop

DRS

Fastest Lap

Rain

Engine Failure

Never clutter charts.

---

# Accessibility

Charts must remain understandable

without color.

Differentiate using

Patterns

Opacity

Labels

Markers

Not color alone.

---

# Performance

Charts should remain smooth

with large datasets.

Prioritize responsiveness over visual complexity.

---

# Recognition Test

If every logo disappears,

users should recognize

Pit Wall Insight

from

Chart Typography

↓

Grid

↓

Tooltip

↓

Crosshair

↓

Animation

↓

Spacing

↓

Telemetry Styling

---

# Do

✓ Keep charts minimal.

✓ Let data dominate.

✓ Use constructor accents intelligently.

✓ Maintain engineering precision.

✓ Keep interactions consistent.

✓ Animate progressively.

---

# Don't

✗ Rainbow colors.

✗ Thick grids.

✗ Heavy shadows.

✗ Decorative gradients.

✗ Random chart libraries.

✗ Different chart styles.

✗ Floating tooltips.

---

# Final Principle

A chart should never look like a chart.

It should feel like an instrument.

The user should feel less like they are reading analytics,

and more like they are operating the telemetry system of a Formula One team.