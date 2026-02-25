# Figma-Inspired Light Redesign Design

## Goal
- Make the mobile app visually close to the referenced Figma task-management style.
- Switch from dark, glass-heavy appearance to a bright UI.
- Keep existing core features and data persistence.
- Ensure timetable is visible at a glance without horizontal scrolling.

## Scope
- Keep menu coverage: existing planner features + timetable.
- Redesign layout/style for strong Figma-like visual identity:
  - bright background
  - purple primary accents
  - rounded cards and soft shadows
  - compact chip and list-card patterns

## Visual System
- Theme mode: `LIGHT` only.
- Palette:
  - Background: very light gray/lilac
  - Surface/Card: white
  - Primary: saturated purple
  - Secondary text: muted gray
  - State chips: pale purple, peach, blue
- Shape:
  - Card radius 16~20
  - Button radius pill style
  - Small icon badges and section chips

## Navigation & Screens
- Use bottom navigation with five destinations:
  - Home
  - Today
  - Add Project
  - Timetable
  - Stats
- Keep data behavior compatible with `DataHandler`.

## Screen Design
- Home:
  - Greeting header
  - Purple summary hero card
  - “In Progress” compact cards
  - Task groups list cards
- Today:
  - Date-strip row
  - Filter chips
  - Task list cards with status badges
- Add Project:
  - Group selector card
  - Name and description inputs
  - Start/end date fields
  - Purple CTA button
- Timetable:
  - Header + subject color legend
  - Add subject form
  - Grid with 월~토 and 0~14교시
  - 0교시: label only
  - 1교시 onward: `HH:00~HH:50`
  - **No horizontal scrolling**: all day columns visible at once on phone width
  - Subject blocks rendered with consistent per-subject colors
- Stats:
  - Card-based progress overview

## Data Flow
- Reuse current `DataHandler` methods.
- No schema break for existing data.
- Timetable color mapping remains by subject key.

## Error Handling
- Input validation before save.
- Show snack-bar errors/success messages.
- Preserve existing fallback error log behavior.

## Verification
- Automated:
  - Existing tests pass.
  - Add regression checks for timetable non-horizontal-scroll implementation.
- Manual:
  - Verify bright look across all destinations.
  - Verify timetable is visible at once without side scroll.
  - Verify add/toggle/delete/save across task and timetable flows.
