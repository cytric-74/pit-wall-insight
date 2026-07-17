# DESIGN SYSTEM

# Pit Wall Insight

Version: 1.0

Status: Planning

---

# Overview

The Pit Wall Insight Design System establishes a single visual language for the entire platform.

Every page, interaction, chart, animation, component, and layout must follow this specification.

The objective is consistency.

Users should immediately recognize that every screen belongs to the same product.

The interface should feel engineered rather than designed.

---

# Design Philosophy

Pit Wall Insight is inspired by:

- Formula One race engineering
- Motorsport telemetry
- Industrial design
- Technical instrumentation
- Apple Human Interface Guidelines
- Nothing Design
- Minimal architecture
- Bloomberg Terminal
- TradingView
- Formula One Live Timing

The interface should communicate:

- Precision
- Speed
- Confidence
- Engineering
- Performance
- Focus

Everything should feel intentional.

Nothing exists purely for decoration.

---

# Design Principles

## Information First

Data is the hero.

Visual elements exist to improve understanding.

---

## Minimalism

Remove unnecessary UI.

Whitespace is a feature.

---

## Motion With Purpose

Every animation communicates state.

Animations should never distract.

---

## Consistency

Every page should feel like part of one product.

Spacing, typography, transitions and interactions remain consistent everywhere.

---

## Engineering Aesthetic

Components resemble professional engineering software.

Not consumer dashboards.

---

# Color System

## Core Palette

### Background

Primary

```
#050505
```

Secondary

```
#0B0B0B
```

Surface

```
#111111
```

Elevated Surface

```
#181818
```

Hover Surface

```
#202020
```

Border

```
#2B2B2B
```

Divider

```
rgba(255,255,255,0.08)
```

---

## Typography

Primary

```
#FFFFFF
```

Secondary

```
#C7C7C7
```

Muted

```
#8D8D8D
```

Disabled

```
#5A5A5A
```

---

## Accent

Default Accent

```
#FF1801
```

Glow

```
rgba(255,24,1,0.30)
```

Danger

```
#E53935
```

Success

```
#00C853
```

Warning

```
#FFC107
```

Info

```
#00B0FF
```

---

# Team Color Tokens

Every Formula One team owns a dedicated theme.

Charts automatically inherit these colors.

Hover effects also inherit them.

Never hardcode colors.

Always use theme tokens.

Example

Ferrari

Primary

```
#DC0000
```

Secondary

```
#FF5A5A
```

Mercedes

Primary

```
#00D2BE
```

Secondary

```
#71FFF2
```

McLaren

Primary

```
#FF8700
```

Secondary

```
#FFBE73
```

Red Bull

Primary

```
#1E5BC6
```

Secondary

```
#5D93F5
```

Aston Martin

Primary

```
#006F62
```

Secondary

```
#4EC5B7
```

Williams

Primary

```
#005AFF
```

Secondary

```
#6EAEFF
```

Alpine

Primary

```
#FF87BC
```

Secondary

```
#FFD0E4
```

Visa Cash App RB

Primary

```
#6692FF
```

Secondary

```
#A9C3FF
```

Haas

Primary

```
#B6BABD
```

Secondary

```
#ECECEC
```

Kick Sauber

Primary

```
#52E252
```

Secondary

```
#A9FFA9
```

---

# Typography

Typography defines hierarchy.

Never rely on font size alone.

Weight and spacing communicate importance.

---

## Display Font

Space Grotesk

Used for

- Hero titles
- Landing pages
- Major headings

---

## Interface Font

Inter

Used for

- Body text
- Navigation
- Labels
- Tables

---

## Data Font

IBM Plex Mono

Used for

- Telemetry
- Numbers
- Statistics
- Timing
- Technical information

---

## LED Font

Dot Matrix Font

Used only for

- Lap time
- Countdown
- Live timing
- Race control displays

Never use for paragraphs.

---

# Font Scale

Display XXL

64px

Display XL

48px

Display

40px

Heading

32px

Sub Heading

24px

Section

20px

Body

16px

Small

14px

Caption

12px

Telemetry

13px

---

# Spacing System

Base Unit

```
8px
```

Allowed spacing

```
4

8

12

16

24

32

40

48

64

96

128
```

Never use arbitrary spacing.

---

# Border Radius

Cards

20px

Buttons

14px

Inputs

12px

Charts

20px

Tags

999px

---

# Shadows

Default

```
0 10px 30px rgba(0,0,0,.25)
```

Large

```
0 20px 60px rgba(0,0,0,.45)
```

Glow

```
0 0 30px rgba(255,24,1,.18)
```

Never overuse glow.

---

# Glass Effect

Glass is subtle.

Never resemble Windows Vista.

Blur

```
16px
```

Opacity

```
0.72
```

Border

```
1px rgba(255,255,255,.06)
```

---

# Grid

Desktop

12 Columns

Max Width

1600px

Content Width

1440px

Sidebar

320px

Gutter

24px

---

# Layout

Persistent Navigation

↓

Content

↓

Analysis Panel

↓

Floating Inspector

Never create crowded layouts.

---

# Icons

Library

Lucide Icons

Rules

- Thin stroke
- Rounded edges
- Consistent sizing

Sizes

16

20

24

28

32

---

# Cards

Cards resemble telemetry modules.

Characteristics

- dark surface
- soft border
- subtle glow
- large radius
- hover elevation

Never use gradients inside cards.

---

# Buttons

Primary

Filled

Secondary

Outline

Ghost

Transparent

Danger

Red

Every button includes

Hover

↓

Elevation

↓

Glow

↓

Smooth Transition

---

# Inputs

Rounded

Dark

Minimal

Animated border

Focus ring

Accent color

Never default browser styles.

---

# Tables

Tables resemble engineering consoles.

Characteristics

- Dense
- Readable
- Hover row
- Sticky headers
- Zebra disabled
- Monospaced numbers

---

# Charts

Charts are first-class UI components.

Never use default chart styles.

Requirements

- Rounded tooltips
- Animated drawing
- Team colors
- Responsive
- Minimal grid
- Soft labels
- No chart junk

---

## Line Charts

Stroke

3px

Curved

Glow on hover

Animated path

---

## Area Charts

Opacity

12%

Gradient

Always

---

## Bar Charts

Rounded

Animated

Hover elevation

---

## Radar Charts

Minimal grid

Accent glow

Thin lines

---

## Heatmaps

Smooth interpolation

Accessible colors

Tooltips

---

## Tooltips

Glass surface

Rounded

Shadow

Monospaced values

Animated fade

---

# Motion

Animation Philosophy

Fast

Intentional

Smooth

Never distracting.

---

## Duration

Instant

100ms

Fast

180ms

Default

240ms

Slow

420ms

Page Transition

650ms

Hero Transition

900ms

---

## Easing

Default

easeOutExpo

Entrance

easeOutQuart

Exit

easeInQuart

Spring

Medium stiffness

---

# Scroll

Smooth scrolling

Lenis

Parallax only where meaningful.

No excessive effects.

---

# Loading

Never use spinning loaders.

Use

- Skeletons
- Progress indicators
- Telemetry initialization
- Number rollups

---

# Cursor

Custom cursor

Small red indicator

Hover expands

Interactive elements respond.

Desktop only.

---

# Accessibility

Contrast AA minimum.

Keyboard navigation.

Visible focus states.

Reduced motion support.

ARIA labels where applicable.

---

# Theme Engine

Entire UI is theme-aware.

Selecting a constructor updates

- Charts
- Accent color
- Buttons
- Hover states
- Progress bars
- Badges
- Timeline
- Telemetry accents
- Active navigation

Typography never changes.

Layout never changes.

Only accent tokens.

---

# Visual Consistency Checklist

Every new component must satisfy:

✓ Uses design tokens

✓ Uses spacing scale

✓ Uses typography scale

✓ Uses motion tokens

✓ Uses border radius system

✓ Uses elevation system

✓ Responsive

✓ Accessible

✓ Theme aware

✓ Dark mode compliant

---

# Engineering Decisions

## Decision 001

Dark Mode Only

Status

✅ Accepted

Reason

Maintains a premium motorsport identity and avoids doubling design complexity.

---

## Decision 002

Token-Based Design System

Status

✅ Accepted

Reason

Ensures consistency, scalability, and easy maintenance.

---

## Decision 003

Constructor-Based Dynamic Themes

Status

✅ Accepted

Reason

Creates a stronger emotional connection while preserving UI consistency.

---

## Decision 004

Charts Follow Team Branding

Status

✅ Accepted

Reason

Improves readability and creates visual continuity throughout the experience.

---

## Decision 005

Motion Is Functional

Status

✅ Accepted

Reason

Animations communicate state rather than acting as decoration.

---

# Definition of Done

The design system is complete when

✓ Every screen uses shared design tokens

✓ No arbitrary colors exist

✓ Typography hierarchy is consistent

✓ Components are reusable

✓ Charts follow the same visual language

✓ Constructor themes work across the platform

✓ Accessibility standards are met

✓ Motion remains smooth and purposeful

✓ The interface feels cohesive from the landing page to the smallest tooltip