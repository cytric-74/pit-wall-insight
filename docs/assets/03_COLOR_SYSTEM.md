# COLOR SYSTEM

# Pit Wall Insight

Version: 1.0

Status: Living Document

---

# Purpose

The Color System defines how color behaves throughout Pit Wall Insight.

Color is never used for decoration.

Color communicates

• State

• Hierarchy

• Interaction

• Team Identity

• Data Relationships

The interface should remain beautiful even in grayscale.

Color enhances understanding.

It never creates it.

---

# Color Philosophy

Pit Wall Insight follows one simple principle.

The interface is monochromatic.

The data is colorful.

Users should remember the information,

not the colors.

---

# Design Principle

90–95% of the interface should use neutral colors.

Only 5–10% should use accent colors.

This makes emphasis meaningful.

---

# Visual Hierarchy

Typography

↓

Spacing

↓

Scale

↓

Position

↓

Color

Color is the final layer of hierarchy.

Never the first.

---

# Neutral Palette

Primary Background

Used across the application.

Deep black.

Pure.

Calm.

---

Secondary Background

Slightly elevated.

Used for sections.

Panels.

Containers.

---

Surface

Cards.

Charts.

Dialogs.

Tables.

---

Elevated Surface

Hovered panels.

Dropdowns.

Context menus.

Floating UI.

---

Hover Surface

Temporary interaction.

Should be subtle.

Never obvious.

---

Borders

Thin.

Low contrast.

Engineering inspired.

Used only to define structure.

---

Dividers

Minimal.

Almost invisible.

Never dominate layouts.

---

# Typography Colors

Primary

Highest emphasis.

Used for

• Headlines

• Statistics

• Active Elements

---

Secondary

Supporting information.

Descriptions.

Subtitles.

Labels.

---

Muted

Metadata.

Units.

Hints.

Supporting information.

---

Disabled

Unavailable actions.

Inactive controls.

Future features.

---

# Semantic Colors

Semantic colors never change.

Regardless of constructor.

---

Success

Green.

Used only for

• Positive Delta

• Fastest Lap

• Improvement

• Completed Actions

---

Warning

Amber.

Used for

• Tyre Wear

• Caution

• Attention

• Fuel Saving

---

Danger

Red.

Used only for

• Critical Errors

• Retirements

• Failures

• Penalties

---

Information

Blue.

Used for

• Notifications

• Guidance

• System Information

---

Purple

Reserved.

Future AI features only.

Never use elsewhere.

---

# Constructor Theme System

Every Formula One constructor owns an identity.

Changing constructors changes the atmosphere.

Not the interface.

---

Constructor themes modify

• Accent

• Chart Colors

• Cursor

• Hero Glow

• Telemetry Lines

• Interactive Highlights

• Active Navigation

• Selection States

Nothing else.

---

# Ferrari

Primary

Ferrari Red

Secondary

Performance Red

Glow

Warm Red

Mood

Aggressive

Focused

Powerful

---

# Mercedes

Primary

Petronas Cyan

Secondary

Ice Cyan

Glow

Cool Cyan

Mood

Precise

Technical

Calm

---

# McLaren

Primary

Papaya Orange

Secondary

Light Orange

Glow

Warm Orange

Mood

Fast

Dynamic

Energetic

---

# Red Bull

Primary

Racing Blue

Secondary

Electric Blue

Glow

Cool Blue

Mood

Confident

Calculated

Dominant

---

# Aston Martin

Primary

British Racing Green

Secondary

Emerald

Glow

Dark Green

Mood

Elegant

Mechanical

Luxury

---

# Williams

Primary

Royal Blue

Secondary

Sky Blue

Glow

Blue Steel

Mood

Minimal

Engineering

Clean

---

# Alpine

Primary

Pink

Secondary

Soft Pink

Glow

Magenta

Mood

Modern

Experimental

---

# Haas

Primary

Steel Gray

Secondary

Silver

Glow

Neutral White

Mood

Industrial

Mechanical

Raw

---

# Racing Bulls

Primary

Azure Blue

Secondary

Light Blue

Glow

Soft Blue

Mood

Modern

Lightweight

Responsive

---

# Sauber

Primary

Neon Green

Secondary

Light Lime

Glow

Green Pulse

Mood

Fresh

Technical

Modern

---

# Theme Transition

Changing constructors should never feel abrupt.

Every color transition should interpolate smoothly.

Duration

500–700ms

No flashes.

No instant swaps.

---

# Chart Color Rules

Charts inherit constructor colors automatically.

Primary Data

Constructor Primary

Comparison

Constructor Secondary

Reference

Neutral White

Historical

Gray

Prediction

Purple

Danger

Semantic Red

Success

Semantic Green

---

# Grid System

Chart grids never inherit constructor colors.

Always remain neutral.

Grid exists to guide.

Not decorate.

---

# Axis

Always neutral.

Never colored.

Only highlight during interaction.

---

# Tooltip

Background

Dark.

Neutral.

Typography

White.

Metadata

Muted.

Highlight

Constructor Accent.

---

# Crosshair

Uses constructor primary.

Opacity remains low.

Should never dominate.

---

# Cursor

Cursor always follows constructor theme.

Ferrari

Red

Mercedes

Cyan

McLaren

Orange

Williams

Blue

etc.

Behavior never changes.

Only color.

---

# Hero Sections

Hero graphics inherit constructor themes.

Background glow

Constructor Accent

Overlay

Neutral

Typography

Always White

The hero should remain readable regardless of theme.

---

# Interactive States

Hover

Accent Border

↓

Accent Glow

↓

Typography Brightens

↓

Cursor Reacts

---

Active

Persistent Accent

High Contrast

Clear Selection

---

Focus

Accessibility first.

Visible.

Consistent.

Never remove focus outlines.

---

Disabled

Muted.

Reduced contrast.

No glow.

No accent.

---

# Shadows

Shadows are never black.

Shadows inherit

Neutral

or

Constructor Accent

depending on context.

Very subtle.

---

# Glow Philosophy

Glow should resemble illuminated instrumentation.

Never neon.

Never bloom.

Never dominate.

Glow supports interaction.

Nothing else.

---

# Gradients

Gradients should remain rare.

Allowed

• Hero Backgrounds

• Constructor Transition

• Ambient Lighting

Not allowed

• Buttons

• Cards

• Tables

• Inputs

• Navigation

---

# Transparency

Transparency creates depth.

Not decoration.

Glassmorphism is prohibited.

Blur is used only where it improves readability.

---

# Data Visualization

Multiple datasets should never become rainbow charts.

Priority

Primary

↓

Secondary

↓

Reference

↓

Historical

↓

Projected

Use shape,

line style,

opacity,

or texture

before introducing additional colors.

---

# Accessibility

Constructor themes must maintain sufficient contrast.

No theme may reduce readability.

No interaction may rely solely on color.

Every state must remain understandable in grayscale.

---

# Do

✓ Keep the interface monochromatic.

✓ Use constructor colors intentionally.

✓ Use semantic colors consistently.

✓ Keep charts calm.

✓ Maintain contrast.

✓ Let data remain the hero.

---

# Don't

✗ Rainbow dashboards.

✗ Random gradients.

✗ Neon glows.

✗ Colorful backgrounds.

✗ Multiple accent colors.

✗ Decorative color usage.

✗ Theme-specific layouts.

---

# Color DNA

The interface should feel

Mechanical

↓

Calm

↓

Technical

↓

Focused

↓

Confident

↓

Premium

Color should whisper.

Never shout.

---

# Final Principle

If every constructor theme is removed,

Pit Wall Insight should still feel complete.

Themes personalize the experience.

They never define it.