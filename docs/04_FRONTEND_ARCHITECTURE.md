# FRONTEND ARCHITECTURE

# Pit Wall Insight

Version: 1.0

Status: Planning

---

# Overview

The frontend is the face of Pit Wall Insight.

It is not designed as a dashboard.

It is designed as an interactive analytics application.

Every screen should feel intentional.

Every animation should communicate state.

Every page should encourage exploration.

The frontend should resemble premium software rather than a collection of charts.

---

# Technology Stack

Core

- React 19
- TypeScript
- Vite

Styling

- TailwindCSS
- shadcn/ui
- tailwind-merge
- clsx

State

- TanStack Query
- Zustand

Animation

- Framer Motion
- Motion One
- Lenis
- GSAP (only when necessary)

Charts

- Apache ECharts
- D3.js

Forms

- React Hook Form
- Zod

Utilities

- date-fns
- React Router
- Lucide Icons

Testing

- Vitest
- React Testing Library
- Playwright

---

# Frontend Philosophy

The frontend should prioritize

- Performance
- Maintainability
- Predictability
- Discoverability
- Delight

No component should exist without a purpose.

---

# Project Structure

```text
apps/frontend/

src/

│
├── app/
│
├── api/
│
├── assets/
│
├── animations/
│
├── components/
│
├── features/
│
├── hooks/
│
├── layouts/
│
├── lib/
│
├── pages/
│
├── routes/
│
├── stores/
│
├── styles/
│
├── themes/
│
├── types/
│
├── utils/
│
├── constants/
│
└── main.tsx
```

---

# Folder Responsibilities

## app/

Application bootstrap.

Responsible for

- Providers
- Theme initialization
- Query Client
- Router
- Global configuration

---

## api/

Contains every API request.

Never perform fetch requests directly inside components.

Example

```
driver.api.ts

constructor.api.ts

race.api.ts

telemetry.api.ts

dashboard.api.ts
```

---

## assets/

Stores

- Images
- SVG
- Logos
- Fonts
- Videos
- Team graphics

---

## animations/

Reusable animation presets.

Example

```
fade.ts

slide.ts

hero.ts

telemetry.ts

charts.ts

page.ts
```

Every page imports animations from here.

Never duplicate animation logic.

---

## components/

Shared reusable UI.

Structure

```
components/

ui/

charts/

tables/

navigation/

cards/

inputs/

layout/

telemetry/

loading/

feedback/

shared/
```

---

# Feature-Based Architecture

Every feature owns its own logic.

```
features/

dashboard/

drivers/

constructors/

races/

telemetry/

strategy/

circuits/

season/

comparison/

settings/
```

Each feature contains

```
components/

hooks/

api/

types/

utils/

pages/
```

Features never depend on each other directly.

---

# Routing

```
/

↓

Landing

↓

Dashboard

↓

Drivers

↓

Constructors

↓

Races

↓

Strategy Lab

↓

Telemetry Center

↓

Circuit Explorer

↓

Season Explorer

↓

Settings
```

Future

```
Predictions

AI Engineer

Live Timing
```

---

# Layout Architecture

Every page follows

```
Header

↓

Navigation

↓

Page Hero

↓

Analytics Content

↓

Supporting Panels

↓

Footer
```

Spacing remains consistent.

---

# Navigation

Persistent Sidebar.

Collapsible.

Contains

- Logo
- Navigation
- Search
- Theme Indicator
- User Preferences (future)

Navigation remains visible.

Never reloads.

---

# Page Structure

Every page consists of

Hero

↓

Filters

↓

Primary Analytics

↓

Supporting Analytics

↓

Related Insights

↓

Footer

---

# Hero Section

Every page begins with a Hero.

Contains

- Large title
- Description
- Breadcrumb
- Context Actions

Example

```
Ferrari

Constructor Analytics

Performance overview for the current season.
```

Hero never exceeds 30% viewport height.

---

# State Management

Global State

Zustand

Contains

- Theme
- Constructor
- Season
- Selected Race
- User Preferences
- Sidebar

---

Server State

TanStack Query

Responsible for

- API Calls
- Caching
- Background Refresh
- Invalidation

Never duplicate server state in Zustand.

---

# Component Hierarchy

Application

↓

Layout

↓

Feature

↓

Section

↓

Card

↓

Visualization

↓

Primitive Components

Never skip layers.

---

# Shared Components

Reusable components include

- Button
- Card
- Badge
- Tooltip
- Tabs
- Modal
- Drawer
- Table
- Search
- Dropdown
- Skeleton
- Empty State
- Error State

Every component supports theming.

---

# Chart Components

Charts are components.

Never directly instantiate charts inside pages.

Example

```
components/

charts/

LineChart

RadarChart

TelemetryChart

Heatmap

TyreChart

SectorChart

ComparisonChart

LapTimeline

RaceReplay

SpeedTrace
```

---

# Constructor Themes

Selecting a constructor automatically updates

- Accent colors
- Chart colors
- Hero gradients
- Button accents
- Progress bars
- Badges
- Active indicators
- Track highlights

Typography never changes.

Layout never changes.

---

# Formula One Cars

Every constructor page includes

Official-inspired vector illustration.

Behavior

Fade

↓

Slide

↓

Glow

↓

Idle floating animation

When constructor changes

Current car exits

↓

New car enters

↓

Theme updates

↓

Charts animate

Transition should feel seamless.

---

# Motion System

Motion should communicate

- hierarchy
- loading
- navigation
- relationships
- transitions

Never animate purely for aesthetics.

---

# Page Transition

Page exits

↓

Background transition

↓

Content fades

↓

Hero enters

↓

Charts animate

↓

Numbers roll

↓

Graphs draw

Maximum

650ms

---

# Scroll Behavior

Lenis Smooth Scroll

Features

- buttery scrolling
- momentum
- section snapping (where appropriate)
- parallax (minimal)

No janky movement.

---

# Microinteractions

Buttons

Hover elevation

↓

Glow

↓

Arrow shift

Cards

Hover lift

↓

Border glow

↓

Shadow

Charts

Hover

↓

Highlight

↓

Tooltip

↓

Guide Line

Numbers

Count-up animation

Progress

Animated fill

---

# Loading Experience

Never use default spinners.

Use

Telemetry initialization

Skeleton screens

Animated placeholders

Progress bars

Live counters

Loading should feel intentional.

---

# Empty States

Every empty state includes

Illustration

↓

Helpful message

↓

Suggested action

Never show blank screens.

---

# Error States

Every error includes

- explanation
- retry action
- support message
- graceful fallback

Never expose raw API errors.

---

# Responsive Strategy

Desktop

Primary experience.

Tablet

Fully supported.

Mobile

Readable.

Not feature identical.

Complex charts adapt.

---

# Performance Budget

First Paint

< 1.5s

Interactive

< 3s

Page Transition

< 300ms perceived

Animation

60 FPS

Bundle

Split by route.

Lazy load heavy charts.

---

# Accessibility

Keyboard navigation.

Visible focus.

Reduced motion support.

Screen reader labels.

Accessible color contrast.

---

# Folder Example

```
features/

drivers/

components/

DriverCard.tsx

DriverHeader.tsx

DriverStats.tsx

DriverComparison.tsx

DriverTelemetry.tsx

DriverCharts.tsx

hooks/

useDriver.ts

useTelemetry.ts

api/

driver.api.ts

types/

driver.types.ts

utils/

driver.utils.ts

pages/

DriverPage.tsx
```

---

# Development Standards

Never

❌ Fetch directly inside components

❌ Duplicate API logic

❌ Duplicate animations

❌ Hardcode colors

❌ Hardcode spacing

❌ Hardcode typography

Always

✅ Use design tokens

✅ Use shared components

✅ Use feature folders

✅ Use reusable hooks

✅ Use typed APIs

---

# Future Enhancements

- PWA support
- Offline mode
- Command Palette
- Keyboard shortcuts
- AI Copilot
- Multi-window analytics
- Multi-monitor layouts

Architecture should support these without redesign.

---

# Engineering Decisions

## Decision 001

Feature-Based Architecture

Status

✅ Accepted

Reason

Improves scalability and ownership.

---

## Decision 002

TanStack Query

Status

✅ Accepted

Reason

Excellent caching, server state management and developer experience.

---

## Decision 003

Zustand

Status

✅ Accepted

Reason

Minimal boilerplate with predictable global state.

---

## Decision 004

Apache ECharts

Status

✅ Accepted

Reason

Highly customizable, performant, and well-suited for engineering-grade visualizations.

---

## Decision 005

Framer Motion First

Status

✅ Accepted

Reason

Consistent animation API with excellent React integration.

GSAP is reserved only for advanced landing experiences where Framer Motion is insufficient.

---

## Decision 006

Feature-Driven Folder Structure

Status

✅ Accepted

Reason

Keeps related code together and simplifies long-term maintenance.

---

## Definition of Done

The frontend is considered complete when

✓ Every page follows the design system

✓ Every feature is isolated

✓ Every API is typed

✓ Every animation is smooth

✓ Every interaction feels intentional

✓ Every component is reusable

✓ Performance targets are achieved

✓ Accessibility standards are met

✓ Constructor themes propagate consistently

✓ The application feels like a premium analytics product rather than a traditional dashboard.