# COMPONENT LIBRARY

# Pit Wall Insight

Version: 1.0

Status: Planning

---

# Overview

The Component Library defines every reusable UI element used throughout Pit Wall Insight.

The goal is to ensure visual consistency, maintainability, accessibility, and scalability.

Every interface should be assembled from reusable components rather than custom-built screens.

No page should introduce unique UI patterns unless they become shared components.

---

# Design Philosophy

Components should feel

- Mechanical
- Premium
- Fast
- Intentional
- Responsive

Every component should communicate confidence.

Animations should feel engineered.

Not playful.

---

# Component Hierarchy

```
Primitive

↓

UI

↓

Shared

↓

Feature

↓

Page

↓

Application
```

Each level depends only on the level below it.

---

# Component Directory

```text
components/

├── ui/
│
├── layout/
│
├── charts/
│
├── telemetry/
│
├── feedback/
│
├── navigation/
│
├── cards/
│
├── data-display/
│
├── overlays/
│
├── forms/
│
├── loading/
│
└── shared/
```

---

# Naming Convention

Every component should use

```
PascalCase
```

Examples

```
DriverCard

ConstructorBanner

LapTimeline

TelemetryChart

PitStopTable
```

Never

```
driverCard

lap-chart

button_new
```

---

# Component Categories

## Primitive Components

Foundation of the UI.

Examples

```
Button

Input

Badge

Avatar

Icon

Divider

Chip

Tooltip

Spinner (rare)

Progress

Checkbox

Switch

Tabs
```

These should never contain business logic.

---

# Layout Components

Responsible for structure.

Components

```
Sidebar

Navbar

PageContainer

Section

Grid

Hero

Footer

ContentWrapper

ResizablePanel

SplitView
```

---

# Navigation Components

```
NavigationItem

SidebarGroup

Breadcrumb

SearchBar

CommandPalette

QuickActions

ThemeSwitcher

SeasonSelector

ConstructorSelector
```

---

# Cards

Cards are the most frequently used component.

Variants

```
AnalyticsCard

TelemetryCard

StatCard

SummaryCard

ComparisonCard

InsightCard

RaceCard

ConstructorCard

DriverCard
```

Rules

- Rounded corners
- Elevated surface
- Subtle border
- Hover animation
- Theme aware

---

# KPI Components

```
StatCard
```

Displays

```
Title

↓

Value

↓

Trend

↓

Description
```

Animated

Count Up

Trend Arrow

Color Transition

---

# Chart Components

Charts are reusable.

Never instantiate ECharts directly inside pages.

Available Components

```
LineChart

AreaChart

BarChart

RadarChart

ScatterChart

Heatmap

TelemetryChart

SectorComparisonChart

LapDeltaChart

TyreStrategyChart

PositionTimelineChart

RaceReplayChart

ChampionshipProgressChart

ConstructorComparisonChart

DriverComparisonChart
```

Every chart supports

- Constructor Theme
- Loading State
- Empty State
- Responsive Resize
- Export
- Tooltip

---

# Table Components

```
TelemetryTable

DriverTable

RaceTable

PitStopTable

ChampionshipTable

ConstructorTable
```

Features

- Sticky header
- Sorting
- Filtering
- Pagination
- Virtualization
- Hover state
- Keyboard navigation

---

# Telemetry Components

Exclusive to Pit Wall Insight.

Components

```
TelemetryGauge

ThrottleMeter

BrakeMeter

Speedometer

GearDisplay

DRSIndicator

RPMMeter

CornerMap

SectorDisplay

TyreWearIndicator

LapDelta

LiveTimingRow
```

These should resemble race engineering software.

---

# Timeline Components

```
RaceTimeline

PitTimeline

WeatherTimeline

SafetyCarTimeline

PositionTimeline

SessionTimeline
```

Features

- Zoom
- Hover
- Replay
- Scroll Sync

---

# Visualization Components

```
TrackMap

RaceReplay

TelemetryReplay

LapReplay

PitWindow

WeatherMap

CircuitElevation

CornerAnalysis
```

Animations should be synchronized.

---

# Hero Components

Every page begins with a Hero.

Hero Variants

```
DashboardHero

DriverHero

ConstructorHero

CircuitHero

RaceHero

TelemetryHero
```

Contains

- Title
- Description
- Metadata
- Quick Actions
- Background Graphic

---

# Constructor Hero

Special component.

Contains

```
Constructor Name

↓

Team Car

↓

Gradient

↓

Statistics

↓

Quick Navigation
```

Selecting another constructor

↓

Car transitions

↓

Theme updates

↓

Charts animate

---

# Formula One Car Component

```
ConstructorCar
```

Properties

```
constructor

theme

animation

size
```

Behaviors

- Fade In
- Slide
- Glow
- Idle Float
- Responsive Scaling

Future

3D Model Support

---

# Filter Components

```
SeasonFilter

RaceFilter

DriverFilter

ConstructorFilter

TyreFilter

CompoundSelector

TrackSelector
```

Rules

Selections update URL.

Selections persist.

---

# Search Components

```
GlobalSearch

QuickSearch

CommandPalette
```

Future

AI Search

Natural Language Search

---

# Feedback Components

```
Toast

Alert

Banner

EmptyState

ErrorState

SuccessState

InfoCard
```

Animations

Fade

Slide

Dismiss

---

# Modal Components

```
Modal

Drawer

BottomSheet

Dialog

ConfirmationDialog

ComparisonDialog
```

Animations

Scale

Opacity

Blur

---

# Loading Components

Never use generic spinners.

Components

```
SkeletonCard

SkeletonChart

SkeletonTable

TelemetryLoader

RaceLoadingScreen

InitializingSequence

NumberRoller

ProgressLoader
```

---

# Empty States

Every feature owns an empty state.

Contains

Illustration

↓

Message

↓

Suggested Action

Never leave blank screens.

---

# Error States

Contains

- Error Code
- Description
- Retry
- Help

Never expose stack traces.

---

# Animation Components

```
AnimatedCounter

AnimatedBorder

AnimatedNumber

Reveal

ParallaxSection

PageTransition

FadeContainer

SlideContainer
```

Shared across application.

---

# Shared Hooks

Components should rely on reusable hooks.

```
useTheme

useBreakpoint

useConstructorTheme

useIntersection

useAnimation

useTooltip

useResize

useChart

useKeyboard

useFilters
```

---

# Props Standards

Every component

Must

- Be typed
- Accept className
- Support theme
- Support loading
- Support accessibility

Should

- Avoid unnecessary props
- Prefer composition

---

# Accessibility

Every component

✓ Keyboard Accessible

✓ Focus Visible

✓ Screen Reader Friendly

✓ Reduced Motion Compatible

✓ High Contrast Compatible

---

# Theme Awareness

Every component automatically adapts

Constructor

↓

Accent Colors

↓

Charts

↓

Buttons

↓

Icons

↓

Badges

↓

Progress

↓

Hero

Only accent colors change.

Layout remains identical.

---

# Motion Standards

Hover

150ms

Click

100ms

Entrance

300ms

Page

650ms

Charts

600ms

Numbers

700ms

Never exceed

1000ms

---

# Performance Standards

Every component

- Lazy load when appropriate
- Memoized where beneficial
- Tree shake friendly
- Reusable
- Independent

Avoid unnecessary re-renders.

---

# Component Documentation

Every shared component includes

Purpose

Props

Variants

Examples

Accessibility Notes

Performance Notes

Future Enhancements

Storybook support planned.

---

# Future Components

```
AIInsightCard

PredictionPanel

VoiceCommand

RaceEngineerAssistant

TelemetryConsole

LiveTimingPanel

TrackHeatmap

SectorReplay

MultiWindowLayout

AnalyticsWorkspace
```

Architecture should support these additions.

---

# Engineering Decisions

## Decision 001

Composition Over Inheritance

Status

✅ Accepted

Reason

Improves flexibility and component reuse.

---

## Decision 002

Feature-Specific Components

Status

✅ Accepted

Reason

Encapsulates domain logic while keeping primitives reusable.

---

## Decision 003

Shared Animation System

Status

✅ Accepted

Reason

Maintains consistent motion across the application.

---

## Decision 004

Theme-Aware Components

Status

✅ Accepted

Reason

Allows constructor branding without duplicating UI components.

---

## Decision 005

Charts as First-Class Components

Status

✅ Accepted

Reason

Charts are central to the product experience and should follow the same standards as every other UI element.

---

# Definition of Done

The component library is complete when

✓ Every repeated UI element exists as a reusable component

✓ Components are fully typed

✓ Components support constructor themes

✓ Accessibility standards are met

✓ Motion follows shared animation tokens

✓ Components are documented

✓ Performance remains optimal

✓ New pages can be built entirely from the component library without creating unnecessary custom UI