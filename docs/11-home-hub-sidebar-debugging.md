# Home Hub Sidebar Debugging

> Documentation of attempted fixes for the collapsible sidebar layout issues in the Home Hub dashboard.

**Status:** RESOLVED
**Date:** January 18-20, 2026
**Dashboard:** `/home-hub/rooms` (and all other home-hub views)

## Problem Description

The Home Hub dashboard has a collapsible sidebar controlled by `input_boolean.sidebar_collapsed`. The sidebar should:
- Be 260px wide when expanded
- Be 64px wide when collapsed
- Have the main content area adjust dynamically when toggling

### Current Issues

1. **Expanded state overlap**: The sidebar overlaps with the main content area instead of the main content starting after the sidebar
2. **Collapsed state gap**: When collapsed, the main content doesn't adjust to fill the space - there's a large gap where the 260px sidebar used to be
3. **Dynamic update failure**: The grid layout doesn't re-render when `input_boolean.sidebar_collapsed` changes state

### Reference Files

- **Mockups**: `/examples/mockup/sidebar-expanded.png` and `/examples/mockup/sidebar-collapsed.png`
- **Debug screenshots**: `/examples/home-hub-debugging/`
- **View files**: `/Volumes/config/dashboards/home-hub/views/*.yaml`
- **Templates**: `/Volumes/config/dashboards/home-hub/button_card_templates.yaml`
- **Decluttering templates**: `/Volumes/config/dashboards/home-hub/decluttering_templates.yaml`

## Architecture

The sidebar uses:
- `custom:layout-card` with `custom:grid-layout` for the two-column layout
- `conditional` cards to swap between expanded/collapsed sidebar templates
- `custom:decluttering-card` for the sidebar templates
- `custom:button-card` for individual sidebar elements

```yaml
# Basic structure in each view file
- type: custom:layout-card
  layout_type: custom:grid-layout
  layout:
    grid-template-columns: [SIDEBAR_WIDTH] 1fr
  cards:
    - type: conditional  # Expanded sidebar (grid-column: 1)
    - type: conditional  # Collapsed sidebar (grid-column: 1)
    - type: vertical-stack  # Main content (grid-column: 2)
```

## Approaches Tried (All Failed)

### Approach 1: CSS Variables with Jinja Templates

**Theory**: Use Jinja to set a CSS variable based on the boolean state, then use that variable in grid-template-columns.

```yaml
card_mod:
  style: |
    :host {
      --hub-sidebar-width: {% if is_state('input_boolean.sidebar_collapsed','on') %}64px{% else %}260px{% endif %};
    }
layout:
  grid-template-columns: var(--hub-sidebar-width, 260px) 1fr
```

**Result**: Failed. The Jinja template is only evaluated once at page load. When the boolean state changes, the CSS variable doesn't update because Jinja doesn't re-evaluate dynamically.

### Approach 2: Direct Jinja in grid-template-columns

**Theory**: Put the Jinja template directly in the grid-template-columns value.

```yaml
layout:
  grid-template-columns: "{% if is_state('input_boolean.sidebar_collapsed','on') %}64px{% else %}260px{% endif %} 1fr"
```

**Result**: Failed. Same issue - Jinja only evaluates at page load, not when state changes.

### Approach 3: min-content for First Column

**Theory**: Use `min-content` to let the grid column size itself based on the minimum content width.

```yaml
layout:
  grid-template-columns: min-content 1fr
```

**Result**: Failed. The column sized to the absolute minimum width, causing text truncation ("Cale...", "Devi...", etc.). The expanded sidebar became too narrow.

### Approach 4: max-content for First Column

**Theory**: Use `max-content` to let the grid column size based on the maximum content width, with explicit width constraints on the conditional cards.

```yaml
layout:
  grid-template-columns: max-content 1fr
cards:
  - type: conditional
    card:
      type: custom:decluttering-card
      template: home_hub_sidebar_expanded
      card_mod:
        style: |
          :host {
            width: 260px !important;
            min-width: 260px !important;
            max-width: 260px !important;
          }
```

**Result**: Failed. The grid column still didn't properly constrain to the sidebar width. Overlap persisted in expanded state.

### Approach 5: Width Constraints in Decluttering Templates

**Theory**: Set width constraints at the ha-card level inside the decluttering templates.

```yaml
# In decluttering_templates.yaml
home_hub_sidebar_expanded:
  card:
    type: vertical-stack
    card_mod:
      style: |
        ha-card {
          width: 260px !important;
          min-width: 260px !important;
          max-width: 260px !important;
          overflow: hidden;
        }
```

**Result**: Failed. The ha-card respected the width, but the grid layout still didn't properly allocate the column width.

### Approach 6: box-sizing and max-width on Children

**Theory**: Ensure child elements don't exceed parent width using box-sizing and max-width.

```yaml
ha-card > * {
  max-width: 260px;
  box-sizing: border-box;
}
```

**Result**: Failed. Didn't affect the grid column sizing.

## Final Solution (Works Reliably)

We stopped trying to resize a single grid at runtime and instead swap two complete layout-card grids. This forces a full reflow and eliminates overlap/gaps in both states.

Pattern used (per view):

1) One top-level card only (panel view requirement):
```
type: panel
cards:
  - type: vertical-stack
    cards:
      - <expanded-conditional-layout>
      - <collapsed-conditional-layout>
```

2) Expanded layout (260px) and Collapsed layout (64px) are separate `custom:layout-card`s:
```
- type: conditional
  conditions:
    - entity: input_boolean.sidebar_collapsed
      state: "off"
  card:
    type: custom:layout-card
    layout_type: custom:grid-layout
    layout:
      grid-template-columns: 260px 1fr
      grid-gap: 16px
      margin: 0
      padding: 0
    cards:
      - type: custom:decluttering-card
        template: home_hub_sidebar_expanded
      - type: custom:decluttering-card
        template: home_hub_<view>_main

- type: conditional
  conditions:
    - entity: input_boolean.sidebar_collapsed
      state: "on"
  card:
    type: custom:layout-card
    layout_type: custom:grid-layout
    layout:
      grid-template-columns: 64px 1fr
      grid-gap: 16px
      margin: 0
      padding: 0
    cards:
      - type: custom:decluttering-card
        template: home_hub_sidebar_collapsed
      - type: custom:decluttering-card
        template: home_hub_<view>_main
```

3) Main content is extracted into a decluttering template (e.g. `home_hub_rooms_main`). The template returns a single `vertical-stack` (one card) and applies:
```
view_layout:
  grid-column: 2
card_mod:
  style: |
    :host { padding: 24px 32px; background: #F9FAFB; min-height: calc(100vh - 48px); }
```

Result:
- No overlap. A fixed 16px gap separates the rail and content.
- No panel warnings (“two cards shown”).
- Collapsed rail centers content correctly at 64px; content shifts flush left.

## What Works Now

1. Two-static-layouts approach with conditional swapping (forces grid reflow)
2. Single top-level card in panel view (silences panel warning)
3. Explicit `grid-gap: 16px` (prevents visual overlap/shadow bleed)
4. Main content pinned to column 2 via `view_layout`

## What Didn't Work (Keep for Reference)

1. CSS variables + Jinja (and JS) to drive `grid-template-columns` dynamically — Jinja evaluates once and layout-card didn’t reliably reflow.
2. Direct Jinja inside `grid-template-columns` — same runtime re-evaluation issue.
3. `max-content` / `min-content` heuristics — produced overlap or truncation and inconsistent widths.
4. Width constraints inside the sidebar only — grid column still failed to allocate correct space.
5. include-based partial injected as a YAML list — caused “No card type configured” under layout-card; replaced with decluttering template returning a single card.

## Current Rollout Status

- Implemented: Rooms (fully migrated to the new pattern)
- Pending: Calendar, Tasks, Meals, Devices, Family, Toby (apply same pattern with per-view `home_hub_<view>_main` templates)

## Next Steps to Update Other Views

For each view in `/Volumes/config/dashboards/home-hub/views/`:
1. Extract the main content into a decluttering template `home_hub_<view>_main` that returns a single `vertical-stack` and sets `view_layout.grid-column: 2`.
2. Replace the view root with a single top-level `vertical-stack` containing two conditional layout-cards (260px and 64px) using the sidebars + the new main template.
3. Set `grid-gap: 16px`, `margin: 0`, `padding: 0` for both layouts.

Note: Ensure `/Volumes/config/` is mounted before editing. See CLAUDE.md → Samba mounting.

## Potential Next Steps

### 1. Force Page Reload
Add a tap_action that reloads the page after toggling the boolean:
```yaml
tap_action:
  action: call-service
  service: input_boolean.toggle
  service_data:
    entity_id: input_boolean.sidebar_collapsed
  # Then somehow trigger window.location.reload()
```

### 2. Use browser_mod for Navigation
Navigate to the same page after toggle to force re-render:
```yaml
tap_action:
  action: fire-dom-event
  browser_mod:
    service: browser_mod.sequence
    data:
      sequence:
        - service: input_boolean.toggle
          data:
            entity_id: input_boolean.sidebar_collapsed
        - service: browser_mod.navigate
          data:
            path: /home-hub/rooms
```

### 3. Single Sidebar with CSS-based Collapse
Instead of swapping conditional cards, use a single sidebar that changes its CSS based on state:
- Use `card_mod` with Jinja to apply different classes
- Use CSS transitions for smooth animation
- May require custom JavaScript via `card_mod`

### 4. Different Layout Approach
Instead of CSS Grid, try:
- Flexbox layout
- Absolute positioning with CSS transitions
- A custom card that handles the sidebar logic

### 5. Investigate layout-card Behavior
- Check if `layout-card` has known issues with dynamic grid changes
- Look for alternative layout cards that support dynamic sizing
- Consider if `custom:grid-layout` vs other layout types behave differently

### 6. Custom JavaScript Solution
Use `card_mod` to inject JavaScript that listens for state changes and manually updates grid-template-columns:
```yaml
card_mod:
  style: |
    /* CSS here */
  # May need to explore if card_mod supports script injection
```

## Files Modified During Debugging

All changes are still in place as of this writing:

- `/Volumes/config/dashboards/home-hub/views/rooms.yaml`
- `/Volumes/config/dashboards/home-hub/views/tasks.yaml`
- `/Volumes/config/dashboards/home-hub/views/calendar.yaml`
- `/Volumes/config/dashboards/home-hub/views/devices.yaml`
- `/Volumes/config/dashboards/home-hub/views/meals.yaml`
- `/Volumes/config/dashboards/home-hub/views/family.yaml`
- `/Volumes/config/dashboards/home-hub/views/toby.yaml`
- `/Volumes/config/dashboards/home-hub/button_card_templates.yaml`
- `/Volumes/config/dashboards/home-hub/decluttering_templates.yaml`

## Current State of Code (Updated Jan 20, 2026)

### View Files (converted views: Rooms, Calendar, Tasks, Devices, Family)
```yaml
layout:
  grid-template-columns: 198px 1fr
  grid-gap: 16px
```

### Pending Views (Meals, Toby)
Still using old pattern:
```yaml
layout:
  grid-template-columns: max-content 1fr
```

### Sidebar Width Constraints
- Expanded: **198px** (in decluttering template and view grid-template-columns)
- Collapsed: 64px (in decluttering template and view grid-template-columns)

### Weather Widget
- Width: **188px** (matches nav item width)
- Margin: 8px 16px

### Nav Items
- Grid: `28px auto` (changed from `28px 1fr` so they don't expand unnecessarily)
- Margin: 2px 16px

## Jan 20 Session: YAML Structure Fixes

During Jan 20 debugging, discovered YAML structure corruption in `decluttering_templates.yaml`:

1. **`home_hub_rooms_main`** - Was missing its `cards:` array entirely. The rooms content (header, scene buttons, room grid) was orphaned at the end of the file. Fixed by adding the cards back to the template.

2. **`home_hub_calendar_main`** - Was missing month view conditionals. They had been accidentally placed inside `home_hub_family_main`. Fixed by moving them to the correct template.

3. **`home_hub_family_main`** - Had misplaced calendar month view content AND orphaned rooms content. Fixed by removing the misplaced content.

These issues caused:
- Rooms view: "Invalid configuration" error (vertical-stack with no cards)
- Calendar view: Month toggle showed blank (month view code was in wrong template)

## Resolved: Weather Widget Content Alignment

The weather widget content was **right-justified** inside the card due to button-card's internal grid layout.

### What We Tried (Did Not Work)
1. `styles.grid.justify-items: start` - No effect
2. `styles.grid.justify-content: start` - No effect
3. `styles.grid.grid-template-columns: 1fr` - No effect
4. `styles.custom_fields.weather_content.justify-self: start` - Only affected "Sunny" text

### Root Cause
Button-card creates an internal grid with `grid-template-columns: 40px 0px 113px` even when `show_icon: false`. The ~40px column reserves space for an icon that doesn't exist, pushing content to the right.

### Fix (March 20, 2026)
Added `grid-template-areas: '"weather_content"'` to `styles.grid` alongside the existing `grid-template-columns: 1fr`. The `grid-template-areas` directive forces button-card's internal grid into a single named area, overriding the shadow DOM's default three-column slot allocation. This is the same pattern used in the "Button-card custom_fields width fix" documented in project memory.

---

*Document created: January 18, 2026*
*Updated: March 20, 2026*
