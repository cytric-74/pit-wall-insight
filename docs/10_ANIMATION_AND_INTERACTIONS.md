# ANIMATIONS & INTERACTIONS

# Pit Wall Insight

Version: 1.0

Status: Planning

---

# Overview

Motion is a core part of Pit Wall Insight.

Animations are not decorative.

They communicate hierarchy, relationships, transitions, loading states, focus, and user intent.

Every animation should reinforce the feeling that users are interacting with a professional race engineering platform.

The application should feel alive without becoming distracting.

Users should remember the experience because of its smoothness—not because animations were excessive.

---

# Motion Philosophy

Every animation must satisfy at least one of the following:

- Explain
- Guide
- Confirm
- Emphasize
- Reduce cognitive load

If an animation serves none of these purposes, it should not exist.

---

# Motion Characteristics

The application should feel

- Fast
- Responsive
- Precise
- Technical
- Premium
- Mechanical

Avoid

- Bouncy animations
- Cartoon motion
- Excessive scaling
- Long delays
- Random movement

Motion should resemble telemetry.

---

# Motion Principles

## Principle 1

Motion should reveal information.

Never hide information.

---

## Principle 2

Animation begins immediately.

No unnecessary delays.

---

## Principle 3

Animations should never block interaction.

Users remain in control.

---

## Principle 4

Motion reinforces hierarchy.

Large elements move first.

Small details follow.

---

## Principle 5

Consistency.

Every animation follows the same timing system.

---

# Timing System

Instant

```
100ms
```

Hover

```
150ms
```

Selection

```
180ms
```

Component

```
240ms
```

Card

```
300ms
```

Chart

```
450ms
```

Page

```
650ms
```

Hero

```
900ms
```

Maximum

```
1000ms
```

Nothing should exceed one second.

---

# Easing

Default

```
easeOutExpo
```

Enter

```
easeOutQuart
```

Exit

```
easeInQuart
```

Spring

Medium stiffness.

Low bounce.

---

# Landing Experience

Landing should create anticipation.

Sequence

```
Background fades

↓

Grid appears

↓

Logo fades

↓

Headline types

↓

Telemetry line scans

↓

CTA appears

↓

Car silhouette fades

↓

Ambient particles activate
```

Entire sequence

~2.5 seconds

User can skip immediately.

---

# Page Transition

Transition sequence

```
Current Page

↓

Fade

↓

Content slides

↓

Background shifts

↓

Hero appears

↓

Cards animate

↓

Charts draw

↓

Numbers roll

↓

Interactions enabled
```

Never hard refresh pages.

---

# Navigation

Sidebar

Hover

↓

Expand

↓

Reveal label

↓

Icon glows

Active item

↓

Accent bar grows

↓

Background fades

↓

Text brightens

---

# Hero Animation

Every Hero follows

```
Background

↓

Title

↓

Subtitle

↓

Metadata

↓

Action Buttons

↓

Statistics

↓

Hero Illustration
```

Never animate everything simultaneously.

---

# Constructor Transition

Selecting another constructor triggers

```
Current Theme

↓

Current Car exits

↓

Accent colors interpolate

↓

Background glow changes

↓

Charts recolor

↓

Statistics update

↓

New Car enters

↓

Telemetry refreshes
```

Entire transition

<700ms

---

# Formula One Car

Every constructor owns its own hero vehicle.

Animation

```
Opacity

↓

Translate

↓

Glow

↓

Idle Float

↓

Ambient Reflection
```

Idle movement

Very subtle.

Approximately

2–4px

Never distracting.

---

# Cards

Entrance

```
Opacity

↓

Translate Y

↓

Blur Reduction
```

Hover

```
Lift

↓

Border Glow

↓

Shadow

↓

Cursor Update
```

Click

```
Compression

↓

Release
```

---

# Buttons

Hover

```
Glow

↓

Background Shift

↓

Arrow Slide

↓

Border Brighten
```

Click

```
Scale 98%

↓

Release
```

Disabled

Opacity only.

No animation.

---

# Numbers

Every important metric animates.

Examples

```
145

↓

001

↓

028

↓

094

↓

145
```

Uses easing.

Never linear.

---

# KPI Cards

Loading

↓

Skeleton

↓

Value counts

↓

Trend appears

↓

Description fades

---

# Charts

Charts should animate as though they are being plotted live.

Never simply appear.

---

## Line Charts

Stroke draws.

Area fades.

Points appear.

Tooltip follows curve.

---

## Area Charts

Fill grows upward.

Opacity increases.

Gradient fades.

---

## Bar Charts

Bars rise independently.

Largest bars finish first.

---

## Radar Charts

Grid fades.

Axis labels appear.

Polygon expands.

Glow activates.

---

## Heatmaps

Cells fade sequentially.

Tooltip reveals on hover.

---

## Pie Charts

Sweep animation.

Labels fade.

Center metric counts upward.

---

# Chart Interaction

Hover

↓

Highlight Series

↓

Dim Others

↓

Guide Line Appears

↓

Tooltip

↓

Crosshair

Leaving chart

↓

Reset smoothly.

---

# Tooltip

Tooltip

```
Fade

↓

Scale

↓

Blur

↓

Content Reveal
```

Never snap instantly.

---

# Tables

Rows

Fade upward.

Hover

↓

Background

↓

Border

↓

Glow

Selection

↓

Accent Bar

↓

Checkbox Animation

---

# Filters

Dropdown

↓

Expand

↓

Blur

↓

Fade

Selection

↓

Checkmark

↓

Collapse

↓

Refresh Results

---

# Search

Focus

↓

Border

↓

Glow

↓

Placeholder fades

↓

Suggestions slide

Keyboard navigation fully animated.

---

# Command Palette

Open

```
Background Blur

↓

Palette Scale

↓

Fade

↓

Cursor Focus
```

Close

Reverse.

---

# Modals

Backdrop

↓

Blur

↓

Fade

↓

Modal Scale

↓

Content Reveal

Escape closes.

---

# Drawer

Slides from edge.

Never fades from center.

---

# Tabs

Indicator glides.

Content crossfades.

No flashing.

---

# Accordions

Height

↓

Opacity

↓

Content

Never abrupt.

---

# Timeline

Race timeline

Scrolls horizontally.

Markers animate.

Hover expands event.

Selecting lap

↓

Entire dashboard synchronizes.

---

# Race Replay

Most important interaction.

Timeline

↓

Current Lap

↓

Track Position

↓

Telemetry

↓

Weather

↓

Pit Stops

↓

Charts

↓

Position Graph

Everything updates together.

No individual refreshes.

---

# Telemetry Replay

Speed trace

↓

Throttle

↓

Brake

↓

Gear

↓

DRS

↓

Mini Track Position

Replay synchronized.

Supports

Play

Pause

Seek

Keyboard

---

# Scroll Experience

Powered by Lenis.

Features

- Smooth interpolation
- Momentum
- Scroll restoration
- Section snapping where appropriate

Parallax kept minimal.

---

# Cursor

Desktop only.

Default

Small red dot.

Hover

↓

Expand

↓

Label

Examples

```
OPEN

VIEW

ANALYZE

COMPARE
```

Never interfere with accessibility.

---

# Background

Background should never be static.

Contains

- Carbon fiber texture
- Noise layer
- Animated grid
- Ambient glow
- Gradient drift

Movement

Extremely subtle.

---

# Ambient Motion

Very low opacity.

Examples

Moving particles

Soft scanlines

Gradient breathing

Track outline glow

Barely noticeable.

---

# Sound (Future)

Optional.

Muted by default.

Possible events

Button click

Telemetry start

Replay play

Success

No continuous background audio.

---

# Reduced Motion

Users with reduced motion enabled receive

- No parallax
- No floating objects
- Instant transitions
- Static backgrounds
- Reduced chart animations

Accessibility takes priority.

---

# Performance Budget

Target

60 FPS

Animation CPU

<10%

GPU acceleration where appropriate.

Never animate

Width

Height

Top

Left

Prefer

Transform

Opacity

Filter (limited)

---

# Animation Utilities

Shared animation library

```
fadeIn()

fadeOut()

slideUp()

slideDown()

pageTransition()

heroReveal()

numberRoll()

chartDraw()

cardHover()

constructorTransition()

telemetryReplay()

timelineReveal()
```

Never duplicate animation logic.

---

# Future Motion

Planned

3D Car Viewer

Track Flyover

Pit Stop Simulation

Live Timing Animation

AI Assistant Motion

Telemetry Streaming

WebGL Track Visualizations

Motion architecture should support future additions.

---

# Engineering Decisions

## Decision 001

Framer Motion as Primary Motion Engine

Status

✅ Accepted

Reason

Excellent React integration with declarative animation architecture.

---

## Decision 002

Motion is Functional

Status

✅ Accepted

Reason

Animations communicate information rather than decorating the interface.

---

## Decision 003

Shared Motion Library

Status

✅ Accepted

Reason

Ensures consistency and avoids duplicated animation implementations.

---

## Decision 004

Constructor Theme Transitions

Status

✅ Accepted

Reason

Creates a cohesive experience while reinforcing team identity.

---

## Decision 005

Performance Before Effects

Status

✅ Accepted

Reason

Smooth interaction is more important than visually impressive animations.

---

# Definition of Done

The animation system is complete when

✓ Every page transition is fluid

✓ Motion follows shared timing tokens

✓ Constructor transitions are seamless

✓ Charts animate consistently

✓ Hover interactions feel responsive

✓ Loading states are informative

✓ Reduced motion is fully supported

✓ Animations maintain 60 FPS

✓ Motion enhances understanding rather than distracting from the data

✓ The entire application feels like a premium engineering product rather than a traditional dashboard