# DESIGN TOKENS

# Pit Wall Insight

Version: 1.0

Status: Living Document

---

# Purpose

Design Tokens are the single source of truth for the visual language of Pit Wall Insight.

Every spacing value.

Every font.

Every animation.

Every color.

Every radius.

Every shadow.

Every layer.

Every component.

Everything should reference tokens.

Never hardcode design values.

---

# Philosophy

Consistency scales.

Tokens allow the interface to evolve without losing identity.

If a value is repeated,

it should become a token.

---

# Token Hierarchy

Brand

↓

Theme

↓

Foundation

↓

Semantic

↓

Component

↓

Page

Never skip layers.

---

# Naming Convention

Every token should be

Readable

Predictable

Scalable

Examples

background-primary

surface-panel

surface-hover

text-primary

text-secondary

text-muted

border-default

border-hover

accent-primary

accent-secondary

---

# Color Tokens

## Background

background-primary

background-secondary

background-tertiary

background-overlay

background-modal

---

## Surface

surface-primary

surface-secondary

surface-elevated

surface-hover

surface-active

---

## Typography

text-primary

text-secondary

text-muted

text-disabled

text-inverse

---

## Borders

border-default

border-subtle

border-hover

border-active

border-focus

---

## Accent

accent-primary

accent-secondary

accent-glow

accent-hover

accent-active

---

## Semantic

success

warning

danger

info

neutral

---

# Constructor Tokens

Each constructor exposes

constructor-primary

constructor-secondary

constructor-glow

constructor-chart

constructor-cursor

constructor-ambient

constructor-gradient

Components never directly reference

Ferrari Red

Mercedes Cyan

etc.

They only reference

constructor-primary

This allows instant theme switching.

---

# Typography Tokens

display-xl

display-lg

display-md

heading-xl

heading-lg

heading-md

heading-sm

body-lg

body-md

body-sm

label-lg

label-md

label-sm

caption

telemetry

code

---

# Font Tokens

font-display

font-body

font-mono

font-dotmatrix

---

# Weight Tokens

weight-light

weight-regular

weight-medium

weight-semibold

weight-bold

---

# Tracking Tokens

tracking-tight

tracking-normal

tracking-wide

tracking-telemetry

tracking-display

---

# Line Height Tokens

leading-tight

leading-normal

leading-relaxed

---

# Spacing Tokens

space-0

space-1

space-2

space-4

space-6

space-8

space-12

space-16

space-20

space-24

space-32

space-40

space-48

space-64

All spacing should use these values.

Never arbitrary margins.

---

# Radius Tokens

radius-none

radius-xs

radius-sm

radius-md

radius-lg

radius-xl

radius-full

Use sparingly.

Avoid large rounded corners.

---

# Border Tokens

border-thin

border-default

border-focus

border-active

Never create new border styles.

---

# Shadow Tokens

shadow-none

shadow-sm

shadow-md

shadow-lg

shadow-panel

shadow-dialog

shadow-floating

Shadows should remain subtle.

---

# Blur Tokens

blur-xs

blur-sm

blur-md

blur-lg

Blur is reserved for overlays and dialogs.

---

# Opacity Tokens

opacity-0

opacity-10

opacity-20

opacity-40

opacity-60

opacity-80

opacity-100

Never use random opacity values.

---

# Animation Tokens

duration-instant

duration-fast

duration-normal

duration-slow

duration-theme

---

# Easing Tokens

ease-standard

ease-in

ease-out

ease-in-out

ease-telemetry

---

# Scale Tokens

scale-hover

scale-active

scale-pressed

Very subtle.

Never exceed 1.03x.

---

# Z-Index Tokens

z-background

z-content

z-header

z-sidebar

z-dropdown

z-tooltip

z-modal

z-toast

z-overlay

Never use arbitrary z-index values.

---

# Grid Tokens

grid-columns

grid-gap

container-width

content-width

reading-width

---

# Breakpoints

mobile

tablet

laptop

desktop

ultrawide

Never design for fixed resolutions.

---

# Component Tokens

Buttons

button-height

button-padding

button-radius

button-gap

Cards

card-padding

card-gap

card-radius

card-border

Charts

chart-grid

chart-axis

chart-tooltip

chart-padding

Navigation

nav-height

nav-width

nav-gap

Sidebar

sidebar-width

sidebar-collapsed

sidebar-padding

---

# Cursor Tokens

cursor-size

cursor-ring

cursor-transition

cursor-crosshair

cursor-glow

---

# Chart Tokens

chart-primary

chart-secondary

chart-grid

chart-axis

chart-crosshair

chart-tooltip

chart-annotation

chart-padding

---

# Hero Tokens

hero-height

hero-overlay

hero-gradient

hero-spacing

hero-title

hero-subtitle

---

# Layout Tokens

container-max

section-gap

content-gap

panel-gap

page-padding

page-margin

---

# Theme Tokens

theme-accent

theme-secondary

theme-glow

theme-shadow

theme-gradient

theme-particle

theme-overlay

---

# Motion Tokens

motion-hover

motion-click

motion-page

motion-chart

motion-dialog

motion-theme

motion-tooltip

---

# Accessibility Tokens

focus-ring

focus-offset

contrast-high

contrast-normal

reduced-motion

---

# Responsive Tokens

mobile-padding

tablet-padding

desktop-padding

sidebar-breakpoint

grid-breakpoint

---

# Design Token Rules

Every visual value must come from a token.

Never

Hardcode colors.

Hardcode spacing.

Hardcode animation timing.

Hardcode border radius.

Hardcode typography.

---

# Implementation Philosophy

Design Tokens should become

CSS Variables

↓

Tailwind Theme

↓

Figma Variables

↓

Component Library

↓

Documentation

Everything references one source.

---

# Future Expansion

New constructors

↓

New components

↓

New pages

↓

New themes

should require

new tokens,

not rewritten code.

---

# Do

✓ Create reusable tokens.

✓ Maintain consistent naming.

✓ Build scalable foundations.

✓ Keep tokens semantic.

✓ Separate implementation from design.

---

# Don't

✗ Hardcoded values.

✗ Duplicate variables.

✗ Arbitrary spacing.

✗ Random animation durations.

✗ Component-specific colors.

---

# Recognition

Even though users never see Design Tokens,

they ensure that every part of Pit Wall Insight feels like one cohesive product.

Consistency is the invisible layer of great design.

---

# Final Principle

Design Tokens are the engineering blueprint of the interface.

They transform a collection of components into a coherent design system.

Every pixel should ultimately trace back to a token.