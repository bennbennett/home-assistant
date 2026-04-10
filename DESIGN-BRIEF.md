# The Countertop — Design Brief

## What This Is

An interactive HTML mockup (`mockup-countertop.html`) for a Home Assistant tablet dashboard. It will be implemented as a YAML-mode Lovelace dashboard using `custom:button-card`, `browser_mod`, and other HACS cards. The mockup is a design prototype — all interactions are simulated with vanilla JS.

## Physical Context

- **Device:** iPad (10th gen, ~11"), landscape orientation
- **Mount:** Kitchen fridge, roughly chest height
- **Input:** Touch, usually one-handed, sometimes with messy/wet hands
- **Sleep:** Screen sleeps after 2 minutes of inactivity — most interactions are transactions, not sessions
- **App:** Home Assistant iOS companion app in kiosk mode (no browser chrome, no HA header/sidebar)

## Who Uses It

Three-person family, all with ADHD. This is the single most important design constraint.

- **Ben** (dad, ~40s) — Built the system. Power user. Uses lights, calendar, shopping list, timer. Will use every feature.
- **Petra** (mom) — Loses her phone constantly. Primary use: Find Phone button. Also uses calendar and shopping list. Gets overwhelmed by busy interfaces and has difficulty navigating multi-level menus. "Shortcut buttons" was her request — she wants to DO things, not find things.
- **Toby** (son, 10) — Tech-fluent, navigates any 2D interface easily. Uses checklists (school, swimming, hockey), plays with lights, checks weather. Loves the visual timer concept. Would use the "I'm Bored" randomizer more if adding activities were easier.

## The ADHD Design Mandate

Direct quote from Ben: "If it's busy, it's overwhelming, and we'll mentally recoil."

This means:
- **Reduce cognitive load aggressively.** Fewer choices, smarter defaults.
- **No hunting.** If Petra can't find it in 2 seconds, it's in the wrong place.
- **Actions over pages.** The home screen has buttons that DO things, not links to places.
- **Show state, don't just show controls.** Timer shows countdown. Lights show on/off. Dinner shows what's left.
- **Visual calm.** Whitespace is intentional, not decorative. Every element earns its space.
- **The nicer it looks, the more they'll use it.** Aesthetic quality directly drives adoption in this household.

## Architecture

**Max depth: 1.** You are always either on the Home screen or one tap away from it. No sidebar, no tab bar, no navigation tree. Drill-down views have a back arrow. Popups overlay the current view and dismiss.

### Home Screen (the "Countertop")

Three zones:

1. **Header** (~80px): Live clock (Fraunces serif, large), date, weather summary (tappable — opens hourly forecast popup)
2. **Main area**: Split into left (action grid) and right (agenda + dinner pool)
   - **Action grid** (left, ~60%): 3x2 grid of large tap targets — Lights, Add to List, Find Phone, Timer, Calendar, Toby
   - **Secondary nav row**: Below the grid, subtle text links for less-frequent pages (Meals, Ben, Petra). This is the extensibility point — new sections get added here.
   - **Agenda** (right, ~280px): Today's calendar events, tomorrow preview. Tapping opens full Calendar view.
   - **Dinner Pool** (right, below agenda): Compact card showing this week's available meals. Tapping opens the "What's for dinner?" picker.
3. **Scene bar** (~64px): Persistent on EVERY view. Five scene chips: Relax, All Off, Bright, Morning, Good Night. This is the #1 feature — light control is always one tap away regardless of what view you're on.

### Drill-Down Views (4)

Each has: back arrow top-left, view content, persistent scene bar at bottom.

- **Lights**: 3x2 room card grid. Each card shows room name, temperature, light status (on/off indicator). Tap toggles lights. Hold opens brightness/color temp popup. Room cards use colored icon tiles (each room has its own color from the palette).
- **Calendar**: Week/month toggle, week-planner-card (7 days), "Plan Meals" link, "+ Add Event" button.
- **Toby's Corner**: Season-toggled checklists (School, Swimming, Hockey — parents toggle seasons on/off via a manage panel, maybe 4x/year). "I'm Bored" randomizer with activity list backed by a `todo` entity so adding new activities is just typing into a text input.
- **Meals** (accessed from Calendar or secondary nav): "Dinner Pool" model — meals are planned weekly for grocery shopping, but the nightly choice is flexible. Cards show Available / Tonight / Done states. Includes recipe browser.

### Popups (3)

- **Add to List**: Text input, Add button, "View full list" link. Three taps max to add a grocery item.
- **Timer**: Visual countdown disc (terracotta conic-gradient that shrinks clockwise, inspired by Time Timer — designed for ADHD/time blindness). Preset buttons (5/10/15/20/30/45 min). Pause and cancel controls. When active, the Timer button on the home screen transforms to show a mini countdown so you can glance at it without opening the popup.
- **Weather**: Horizontal forecast bar matching `lovelace-hourly-weather` card style — gradient track with weather icon, time/temp labels below at 2-hour intervals.

### Instant Actions (2)

- **Find Phone**: One tap. Rings Petra's iPhone immediately. Toast notification confirms "Ringing Petra's phone..." for 3 seconds. No confirmation dialog, no navigation.
- **Scene chips**: One tap. Fires the scene. Active scene gets a warm tint. Works on every view.

## Visual Language

### Direction: "Warm, Confident Tool"

Evolved from a previous "Editorial Kitchen" direction that used Fraunces serif, 6+ warm-earth accent colors, and magazine-spread styling. That was designed for a 10-view sidebar dashboard. The Countertop is simpler (5 views, 1 level deep), so the visual language was simplified to match:

- **Keep the warmth and character** — this is a family kitchen, not a tech dashboard
- **Simplify the palette** — from 6 accent colors to 3 working colors
- **Fraunces for hero moments only** — clock, page headers, room names. Not for data or labels.
- **System sans for everything functional** — SF Pro / system font for button labels, agenda items, list content. Optimized for scanning speed.
- **One universal card style** — same radius, shadow, border, padding everywhere

### Typography (final — arm's-length optimized for fridge iPad)

| Use | Font | Size | Weight |
|-----|------|------|--------|
| Clock | Fraunces | 46px | 350 |
| Greeting | Fraunces italic | 16px | 350 |
| Page headers (Lights, Calendar, etc.) | Fraunces | 26px | 400 |
| Room names, checklist names | Fraunces | 16px | 450 |
| Recipe Browser label | Fraunces | 19px | 400 |
| Popup titles | Fraunces | 22px | 400 |
| Action button labels | System sans | 15px | 600 |
| Agenda event titles | System sans | 14px | 500 |
| Agenda times | System sans | 13px | 500 |
| Calendar events | System sans | 12px | 500 |
| Calendar day names | System sans | 11px | 600, uppercase |
| Calendar day numbers | Fraunces | 22px | 400 |
| Scene chip labels | System sans | 14px | 500 |
| Secondary nav links | System sans | 14px | 500 |
| Meal card names | System sans | 14px | 600 |
| Dinner pool chips | System sans | 13px | 500 |
| Checklist item text (popup) | System sans | 15px | 500 |
| Eyebrow labels (TODAY, etc.) | System sans | 11-12px | 700, uppercase, tracked |
| Date (header) | System sans | 15px | 500 |
| Weather temp | System sans | 18px | 600 |
| Weather hi/lo | System sans | 13px | 400 |

### Color Palette

Three working colors plus neutrals:

| Token | Hex | Role |
|-------|-----|------|
| **Terracotta** | `#C87456` | "Current moment" — today markers, active timer, tonight's dinner, Find Phone. Also used for the timer disc countdown. |
| Terracotta tint | `#FFF6F1` | Light background for active/current states |
| Terracotta peach | `#FCE9DE` | Badges, pressed states, today indicators |
| **Sage** | `#4A7C59` | "Action" — interactive elements, buttons, navigation, checkmarks, add/submit actions |
| Sage light | `#E8F0EA` | Light background for sage elements |
| **Neutral warm gray** | `#6B7280` | Secondary text, labels, metadata |

Room icon tiles derive their background from each room's accent color at 14% alpha, giving each card a warm tinted tile without adding more "working" colors to the system. The room colors (terracotta, sage, honey `#B89254`, taupe `#8E7065`, clay `#9A6B47`, olive `#6E8E4D`) are cosmetic — they only appear in icon tiles and don't carry semantic meaning.

### Card Tokens

| Property | Value |
|----------|-------|
| Background | `#FFFFFF` |
| Border radius | `16px` |
| Border | `1px solid #F0EDE8` |
| Shadow | `0 1px 3px rgba(0,0,0,0.06)` |
| Page background | `#fbfaf9` (warm off-white) |

### Scene Bar

| Property | Value |
|----------|-------|
| Background | `#F5F3F0` |
| Border top | `1px solid #E5E0DA` |
| Height | `64px` |
| Chip height | `42px` |
| Chip radius | `21px` (full pill) |
| Active chip | Terracotta tint background + 2px terracotta border + terracotta text |

### Icons

All icons are SVG line-style (Lucide-inspired), consistent across every view. No emoji in UI elements. Stroke width 1.8px, round caps and joins. Icons sit in colored tile backgrounds (rounded rectangle, 12-13px radius) with the tile color derived from the semantic context.

### Spacing Scale

All gaps, padding, and margins follow an 8/12/16/24 scale:

| Token | Use |
|-------|-----|
| 8px | Tight gaps (secondary nav, scene chip gap, icon-to-label in buttons) |
| 12px | Card grid gaps (action grid, room grid, meals grid, checklist grid, calendar) |
| 16px | Home main grid gap, card internal padding, agenda card padding |
| 24px | View content horizontal padding, popup internal padding |

### Action Button Sizing

| Property | Value |
|----------|-------|
| Icon tile | 52x52px, border-radius 13px |
| Icon SVG | 28x28px |
| Label | 15px, weight 600 |
| Icon-to-label gap | 8px |
| Grid gap | 12px |
| Home grid split | `1fr 320px`, gap 16px |

### Popup Sizing (arm's-length optimized)

| Property | Value |
|----------|-------|
| Title | 22px Fraunces |
| Close button | 34x34px |
| Input height | 44-48px |
| Input text | 15-16px |
| Submit button height | 44-48px |
| Submit button text | 14-15px |
| Checklist checkbox | 26x26px |
| Checklist item text | 15px |
| Timer presets | 56x44px, 15px |
| Timer disc | 170x170px |
| Timer disc time | 34px |

### Interaction Feedback

- **Tap**: `transform: scale(0.97)` + shadow removal (0.15s ease)
- **Hover** (room cards): `translateY(-2px)` + deeper shadow (0.2s cubic-bezier)
- **Active scene**: Terracotta tint + border color change
- **Toast** (Find Phone): Slides down from top, terracotta background, auto-dismisses after 3s
- **Timer disc**: Conic-gradient in terracotta, shrinks clockwise. Inner circle shows time remaining.

## Design Refinements Applied

The mockup (`mockup-countertop.html`) has been through 3 critique-and-fix cycles, scoring 27 → 29 → **31/40** on Nielsen's heuristics. Key refinements:

- **Home screen rebalance**: Right panel widened to 320px, action button icons scaled to 52px with 15px labels, agenda text bumped for arm's-length readability
- **Subview composition**: Calendar day cells fill the viewport (460px min-height), Lights and Toby views vertically centered, Meals view has populated recipe browser grid
- **Arm's-length typography**: All functional text bumped 1-2px (minimum 11px for eyebrows, 13-15px for body text, 22px for popup titles)
- **Spacing normalization**: All gaps on 8/12/16/24 scale
- **Popup sizing**: Inputs 44-48px height, checkboxes 26px, timer presets 56x44px — all optimized for fridge-distance touch
- **Room card hold affordance**: Subtle `···` grip at bottom of each room card signals hold-for-controls
- **Tonight dinner chip**: Home screen dinner pool highlights tonight's meal in terracotta
- **Active scene chip**: 2px border for better visibility at arm's length
- **Quick-add dinner**: Free-text input in dinner popup ("Takeout, leftovers...") for non-recipe meals — Petra's request
- **Checklist icons**: Per-item colored icon tiles (sparkle, shirt, coffee, box, backpack, droplet, footprints) for visual scanning — Toby's readability need

## Implementation Notes

This mockup is ready to be converted into a YAML-mode Lovelace dashboard. Implementation will use:

- `custom:button-card` for all custom cards (action buttons, room cards, checklist cards, agenda, dinner pool)
- `browser_mod` for popups (Add to List, Timer, Weather, Dinner, Checklist)
- `custom:week-planner-card` for Calendar view
- `kiosk-mode` to hide HA chrome
- `home-hub-fonts.js` pattern for loading Fraunces (already exists)

Key entities needed:
- Scene scripts (Relax, All Off, Bright, Morning, Good Night)
- `sensor.live_time`, `sensor.live_date_long`, `sensor.live_greeting` (reuse from Home Hub)
- `sensor.home_hub_upcoming_events` (reuse from Home Hub)
- `sensor.mealie_weekly_meal_plan`, `sensor.mealie_recipe_browser` (reuse from Home Hub)
- Light entities for all 6 rooms (already exist)
- Temperature sensors (already exist)
- Timer helper entity (new — `timer.kitchen_timer`)
- Toby's checklist entities (reuse `todo.*` entities)
- `input_text.dinner_quick_add` (new — for the quick-add dinner feature)
- `todo.google_keep_shopping_list` (for Add to List popup)

The dashboard should be registered as `mode: yaml` at `/countertop/home` with `kiosk_mode: kiosk: true`.

The audience is a family with ADHD using a kitchen fridge iPad. Calm, warm, confident, functional.
