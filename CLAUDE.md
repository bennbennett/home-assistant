# Home Assistant - Claude Code Context

> This file provides context for Claude Code sessions working with this Home Assistant setup.

## TODO (Cleanup)
- [x] Delete `hass-setup.sh` from root (moved to `tools/`) — done Feb 2026
- [x] Delete `monitor_lights.py` from root (moved to `tools/`) — done Feb 2026
- [x] Delete `session_history.log` from root (archived to `history/sessions/2024-11-13.md`) — done Feb 2026
- [x] Delete stale sensors: `sensor.mealie_recipe_list`, `sensor.mealie_recipe_list_2` — already cleaned up
- [x] ~~Install `auto-entities` HACS card for dynamic recipe grid~~ — not needed; `auto-entities` filters HA entities, but recipes are sensor attribute items. JS templating in button-card is the correct approach.
- [x] Update remaining day cards (Tue-Sun) to use `fire-dom-event` popup pattern — done Feb 2026
- [x] Create automation to sync `input_select.recipe_selector` options with Mealie recipes — done Feb 2026

## Quick Reference

| Item | Value |
|------|-------|
| **HA URL** | `http://192.168.68.114:8123` (works home & remote — remote goes via bennett-server subnet route) |
| **Tailscale access** | Via `bennett-server` (`100.68.225.20`) subnet route for `192.168.68.0/24`. HA's own Tailscale daemon (`100.116.131.121` / `homeassistant.tail7d68ca.ts.net`) is offline as of 2026-04-07. |
| **3D Printer IP** | `192.168.68.103` (Elegoo Centauri Carbon) |
| **Phone** | Pixel 10 (`notify.mobile_app_pixel_10`) |
| **Credentials** | `.env` file (use `. .env` to load) |
| **Config Access** | Samba mount at `/Volumes/config/` |
| **iPad Dashboard** | `/lovelace/ipad` (tablet-dashboard) |
| **Home Hub Dashboard** | `/home-hub/rooms` (home-hub) |
| **Countertop Dashboard** | `/the-countertop/home` (the-countertop) |
| **Mobile Dashboard** | `/mobile-dashboard/home` (mobile-dashboard) |
| **HA Version** | 2026.3.0 |

## Remote Access (Away from Home)

As of 2026-04-07, **the same URL works home and remote** — Tailscale delivers you transparently to the LAN via the bennett-server subnet route. No more separate "local IP" vs "Tailscale IP" switching.

### 1. API Access
```bash
. .env
curl -s -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/"
```

`$HASS_URL` in `.env` should be `http://192.168.68.114:8123` (same from home or remote). If `.env` still has a separate `$HASS_URL_REMOTE` pointing at `100.116.131.121`, that IP is dead — update or remove it.

### 2. Config File Access (Samba)
```bash
open "smb://192.168.68.114/config"
```

Mounts to `/Volumes/config/`. Same URL whether home or away. User will need to authenticate the Samba dialog when it appears.

**Requirements (remote only):**
- Tailscale running on the Mac with `--accept-routes` enabled (`tailscale set --accept-routes=true`)
- bennett-server's `192.168.68.0/24` subnet route approved in the Tailscale admin console (one-time)
- Samba credentials (same as local access)

**Why it works:** HA's own Tailscale daemon (`100.116.131.121`) has been offline since around 2026-04-07. Instead of relying on HA's direct Tailscale presence, bennett-server now acts as a subnet router advertising the whole `192.168.68.0/24` LAN into Tailscale. This is actually more robust — it survives HA crashes, DHCP lease changes, and Tailscale add-on failures on HA.

## Quick Start

### Mount Samba (Claude should do this automatically)
If `/Volumes/config/` is not mounted, Claude should check network and mount:
```bash
# Check if already mounted
ls /Volumes/config/ 2>/dev/null && echo "Mounted" || echo "Not mounted"

# Verify reachability (works home or via Tailscale subnet route when remote)
ping -c 1 -W 1 192.168.68.114 >/dev/null 2>&1 && echo "Reachable" || echo "Unreachable — check Tailscale"

# Mount (same URL home and remote; user will authenticate the Samba dialog)
open "smb://192.168.68.114/config"
```

### API and Commands
```bash
# Load credentials (use dot-sourcing, not 'source' - more reliable)
. .env

# Test connection
curl -s -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/"

# IMPORTANT: For large API responses (like /api/states), always save to file first
# Piping directly to python fails due to buffering issues
. .env && curl -s -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/states" > /tmp/ha_states.json
python3 -c "import json; data=json.load(open('/tmp/ha_states.json')); print(f'Found {len(data)} entities')"

# Use helper script
./tools/hass-setup.sh test
./tools/hass-setup.sh summary
./tools/hass-setup.sh states light
./tools/hass-setup.sh entity light.living_room
./tools/hass-setup.sh service light turn_on '{"entity_id":"light.living_room"}'
```

## System Overview

- **~650 entities** across smart home devices
- **25 automations** (21 enabled, see Key Automations section)
- **Key integrations**: Nest, TP-Link/Kasa, Tuya, Philips Hue, Roomba, ZHA (Zigbee), HACS, Adaptive Lighting, Elegoo Printers, Mealie

### Key Light Entities
| Entity | Description |
|--------|-------------|
| `light.living_room` | Living room lights |
| `light.front_house` | Front house lights (FP2 presence sensor area) |
| `light.bedrooms` | All bedroom lights zone |
| `light.master_bedroom` | Master bedroom |
| `light.toby_s_room` | Toby's room |
| `light.kitchen` | Kitchen lights |
| `light.outdoor_lights_dimmable` | Outdoor string lights (KP405) |
| `light.the_abyss` | 3D Printer LED strip (Hue room) |
| `light.dining_kitchen_zone` | Kitchen + Dining room zone |

### Key Sensors
| Entity | Description |
|--------|-------------|
| `binary_sensor.outside_door` | Outside door sensor |
| `binary_sensor.door_sensor_shed` | Shed door sensor |
| `sensor.living_room_temp_temperature` | Living room temperature |
| `sensor.bedroom_temp_humidity_temperature` | Bedroom temperature |
| `weather.pirateweather` | Weather forecast (PirateWeather integration) |

### Adaptive Lighting Switches
| Switch | Controls |
|--------|----------|
| `switch.adaptive_lighting_living_room` | Living room color temp |
| `switch.adaptive_lighting_kitchen` | Kitchen color temp |
| `switch.adaptive_lighting_toby_room` | Toby's room color temp |
| `switch.adaptive_lighting_bedrooms` | Bedrooms color temp |

### 3D Printer (Elegoo Centauri Carbon)
Integration: [Elegoo Printers (HACS)](https://github.com/danielcherubini/elegoo-homeassistant) - uses SDCP protocol (not Moonraker)

| Entity | Description |
|--------|-------------|
| `sensor.centauri_carbon_print_status` | Current status (idle, printing, complete, etc.) |
| `sensor.centauri_carbon_percent_complete` | Print progress percentage |
| `sensor.centauri_carbon_current_layer` | Current layer number |
| `sensor.centauri_carbon_total_layers` | Total layers in print |
| `sensor.centauri_carbon_remaining_print_time` | Time remaining (minutes) |
| `sensor.centauri_carbon_file_name` | Current file being printed |
| `sensor.centauri_carbon_nozzle_temperature` | Nozzle temp (°F) |
| `sensor.centauri_carbon_bed_temperature` | Bed temp (°F) |
| `sensor.centauri_carbon_box_temp` | Enclosure temp (°F) |
| `camera.centauri_carbon_chamber_camera` | Live chamber camera feed |
| `light.centauri_carbon_chamber_light` | Chamber light control |
| `button.centauri_carbon_pause_print` | Pause current print |
| `button.centauri_carbon_resume_print` | Resume paused print |
| `button.centauri_carbon_stop_print` | Stop current print |

**Print status values:** idle, homing, printing, paused, complete, preheating, leveling, and others

**Dashboard:** Card on iPad Devices view (under "Computer" filter) with popup showing camera, temps, progress, and controls

**Note:** If the printer IP changes (e.g., after router reboot), the Elegoo integration must be deleted and re-added with the new IP in Settings → Devices & Services. The LED automation includes a `from: unavailable` trigger to handle reconnection scenarios.

### Mealie (Meal Planning)
Integration: [Mealie](https://mealie.io/) - Self-hosted recipe manager running on GMKtec server

**Server:** `http://100.68.225.20:9925` (via Tailscale - required for HA Yellow connectivity)
**API Token:** Stored in multiple locations (expires ~2031):
- `.env` (MEALIE_TOKEN, MEALIE_URL) - for local scripts
- `secrets.yaml` (mealie_token, mealie_token_header) - for HA config
**Config Entry ID:** `01KF57HBNBY4RWWRGH5PJKBF1C` (needed for service calls)

**Mealie URL Format (v2):** `/g/home/r/{slug}` (e.g., `http://100.68.225.20:9925/g/home/r/traditional-czech-rizek`)

| Entity | Description |
|--------|-------------|
| `calendar.mealie_breakfast` | Breakfast meal plan calendar |
| `calendar.mealie_lunch` | Lunch meal plan calendar |
| `calendar.mealie_dinner` | Dinner meal plan calendar |
| `todo.mealie_weekly_groceries` | Weekly Groceries shopping list |
| `sensor.mealie_recipes` | Recipe count (from integration) |
| `sensor.mealie_categories` | Category count |
| `sensor.mealie_tags` | Tag count |
| `sensor.mealie_recipe_browser` | Recipe list with full details (trigger-based, populated by automation) |
| `sensor.mealie_weekly_meal_plan` | Weekly meal plan (trigger-based, populated by automation) |

**Helper Entities (for Meals dashboard):**
| Entity | Purpose |
|--------|---------|
| `input_button.sync_shopping_list` | Triggers Mealie → Google Keep sync |
| `input_select.meal_day_selector` | Day picker for meal assignment (Mon-Sun) |
| `input_select.recipe_selector` | Recipe picker dropdown (auto-synced from Mealie by automation) |
| `input_text.recipe_import_url` | URL input for recipe import popup |

**Automations:**
| Automation | Purpose |
|------------|---------|
| `mealie_fetch_recipe_list` | Fetches recipes hourly, fires `mealie_recipes_updated` event |
| `mealie_fetch_mealplan` | Fetches Mon-Sun meal plan every 30 min, transforms to clean dicts, fires `mealie_mealplan_updated` event |
| `mealie_sync_recipe_selector` | Syncs recipe names to `input_select.recipe_selector` on recipe update / HA start |
| `mealie_google_keep_shopping_list_sync` | Syncs Mealie → Google Keep every 20 min |

**Scripts:**
| Script | Purpose |
|--------|---------|
| `script.assign_meal_to_day` | Assigns selected recipe to selected day via `mealie.set_mealplan` |
| `script.import_recipe_from_url` | Imports recipe from URL via `mealie.import_recipe`, clears input, fires refresh |
| `script.clear_meal_for_day` | Clears assigned meal for selected day |
| `script.clear_weekly_groceries` | Removes all items from `todo.mealie_weekly_groceries` (active and completed) |

**CLI Tools:**
| Tool | Purpose |
|------|---------|
| `tools/generate_grocery_list.py` | Generate grocery list from weekly meal plan (supports `--preview`, `--sync`, `--clear`) |
| `tools/import_recipe_pdf.py` | Import recipe PDFs into Mealie |

**Dashboard:**
- iPad: `/tablet-dashboard/meals`
- Home Hub: `/home-hub/meals` (has Recipe Browser grid)

**Recipe Browser (Home Hub):**
- Shows recipe cards in 3-column grid using button-card JavaScript templating
- Data comes from `sensor.mealie_recipe_browser` items attribute
- Recipe cards and category chips use explicit pointer/touch handlers so iPad taps behave like mouse clicks
- Clicking or tapping a recipe opens a browser_mod popup with name, description, times, yield, and source/Mealie links
- "+ Add Recipe" button opens a URL import popup (enters URL → calls `mealie.import_recipe`)

**Grocery Popup (Home Hub):**
- Opens from the Weekly Dinners section header button
- Uses `todo.mealie_weekly_groceries`
- `Clear All` calls `script.clear_weekly_groceries` to remove all items from the list, not just completed ones
- `Send to Keep` triggers the Mealie -> Google Keep sync flow

**Meal Assignment Flow:**
1. Click a day card (e.g., Monday) → sets `input_select.meal_day_selector`
2. Popup opens with recipe dropdown (`input_select.recipe_selector`)
3. Select recipe, click "Assign"
4. Calls `script.assign_meal_to_day` which calls `mealie.set_mealplan`

**Maintenance:** None required — recipe selector options and ID lookups are fully automated via `mealie_sync_recipe_selector` automation and dynamic sensor lookup in `assign_meal_to_day` script.

**Mealplan data serialization:** `mealie.get_mealplan` returns Python objects with `datetime.date` and `MealplanEntryType` enums that don't serialize to JSON. The `mealie_fetch_mealplan` automation transforms these to flat dicts with string-only values (`date`, `title`, `recipe_name`, `recipe_slug`) using a Jinja2 namespace loop before firing the event. This ensures the trigger-based sensor stores a proper list (not a Python repr string) that button-card JavaScript can iterate over.

**Mealie recipe corruption note:** If `GET` or `DELETE /api/recipes/{slug}` returns `500` with a validation error referencing `recipe_ingredient.*.reference_id`, the recipe record is corrupted in Mealie's SQLite DB (`/DATA/AppData/mealie/data/mealie.db`). This happened with `test-import` and `test-import-1` on March 2, 2026. The successful recovery path was: back up the DB, delete the affected rows from `recipes` plus linked rows in `recipes_ingredients`, `recipe_instructions`, `recipe_nutrition`, `recipe_settings`, and `recipe_timeline_events`, then remove the empty recipe folders from `/DATA/AppData/mealie/data/recipes/`.

**Mealplan sensor attribute format:**
```python
# Each item in sensor.mealie_weekly_meal_plan attributes.meals:
{'date': '2026-02-09', 'title': '', 'recipe_name': 'Traditional Czech Řízek', 'recipe_slug': 'traditional-czech-rizek'}
```

**Note:** HA Yellow requires Tailscale TUN mode enabled (not userspace) to reach the GMKtec server. If Mealie integration fails to connect, check Tailscale add-on settings.

## File Structure

```
home-assistant/
├── CLAUDE.md              # This file - read first
├── .env                   # Credentials (HASS_URL, HASS_TOKEN)
├── docs/                  # Detailed documentation
│   ├── INDEX.md          # Documentation navigation
│   └── *.md              # Topic-specific docs
├── tools/                 # Helper scripts
│   ├── hass-setup.sh     # API helper functions
│   ├── monitor_lights.py # Light monitoring utility
│   ├── import_recipe_pdf.py  # Import recipe PDFs into Mealie
│   └── generate_grocery_list.py # Generate grocery list from meal plan
├── examples/              # Code snippets and examples
└── history/               # Session logs and changelog
```

## Configuration Files (Samba)

Mount Samba share: `open "smb://192.168.68.114/config"`

| File | Purpose |
|------|---------|
| `/Volumes/config/automations.yaml` | All automations |
| `/Volumes/config/adaptive_lighting.yaml` | Adaptive Lighting config |
| `/Volumes/config/lights.yaml` | Light templates |
| `/Volumes/config/configuration.yaml` | Main HA config |
| `/Volumes/config/dashboards/` | Dashboard YAML files |
| `/Volumes/config/dashboards/tablet.yaml` | iPad dashboard |
| `/Volumes/config/dashboards/mobile-redesign-v2.yaml` | Mobile dashboard |
| `/Volumes/config/dashboards/views/rooms.yaml` | iPad rooms view |
| `/Volumes/config/dashboards/views/calendar.yaml` | iPad calendar view (week-planner-card) |
| `/Volumes/config/dashboards/views/devices.yaml` | iPad devices view (phones, tablets, printers) |
| `/Volumes/config/dashboards/views/meals.yaml` | iPad meals view (Mealie integration) |
| `/Volumes/config/dashboards/popups/meal_selection_popup.yaml` | Recipe picker popup |
| `/Volumes/config/dashboards/popups/recipe_import_popup.yaml` | URL import popup |
| `/Volumes/config/dashboards/popups/grocery_list_popup.yaml` | Grocery list popup (todo-list + actions) |
| `/Volumes/config/dashboards/popups/calendar_event_popup_home_hub.yaml` | Add Event popup (green palette, Home Hub only) |
| `/Volumes/config/dashboards/button_card_templates.yaml` | Card templates |
| `/Volumes/config/dashboards/home-hub.yaml` | Home Hub dashboard (includes kiosk_mode config) |
| `/Volumes/config/dashboards/countertop.yaml` | Countertop kitchen iPad dashboard |
| `/Volumes/config/dashboards/countertop/` | Countertop templates and views |
| `/Volumes/config/dashboards/home-hub/` | Home Hub templates and views |
| `/Volumes/config/dashboards/home-hub/views/ben.yaml` | Ben's personal subpage |
| `/Volumes/config/dashboards/home-hub/views/petra.yaml` | Petra's personal subpage |
| `/Volumes/config/dashboards/home-hub/views/right_now.yaml` | Right Now landing (default view, glance-first) |
| `/Volumes/config/www/kiosk-mode/kiosk-mode.js` | Kiosk mode JS (hides HA chrome on Home Hub) |
| `/Volumes/config/www/home-hub-fonts.js` | Loads Fraunces serif from Google Fonts + global animation keyframes (hh-pulse, hh-fade-in) |

## Common Tasks

### Query Entities
```bash
# Get all light states (save to file first, then filter)
. .env && curl -s -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/states" > /tmp/ha_states.json
python3 -c "import json; [print(f\"{s['entity_id']}: {s['state']}\") for s in json.load(open('/tmp/ha_states.json')) if s['entity_id'].startswith('light.')]"

# Get all automations
python3 -c "import json; [print(f\"{s['entity_id']}: {s['state']} - {s['attributes'].get('friendly_name','')}\") for s in json.load(open('/tmp/ha_states.json')) if s['entity_id'].startswith('automation.')]"

# Get specific entity (small response, piping OK)
. .env && curl -s -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/states/light.living_room" | python3 -m json.tool
```

### Control Devices
```bash
# Turn on light
curl -X POST -H "Authorization: Bearer $HASS_TOKEN" -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room"}' "$HASS_URL/api/services/light/turn_on"

# Turn on with brightness
curl -X POST -H "Authorization: Bearer $HASS_TOKEN" -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room", "brightness_pct": 50}' "$HASS_URL/api/services/light/turn_on"

# Set color temperature
curl -X POST -H "Authorization: Bearer $HASS_TOKEN" -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room", "color_temp_kelvin": 4000}' "$HASS_URL/api/services/light/turn_on"
```

### Reload Configurations
```bash
# Reload automations
curl -X POST -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/services/automation/reload"

# Reload scripts
curl -X POST -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/services/script/reload"
```

## Key Automations

| Automation | ID | Status | Purpose |
|------------|----|----|---------|
| Hockey Checklist Reset | `hockey_checklist_midnight_reset` | ON | Reset checklist at midnight |
| School Checklist Reset | `reset_school_checklist_at_midnight` | ON | Reset checklist at midnight |
| Hourly Adaptive Temp (All Rooms) | `hourly_adaptive_temp_all_rooms` | ON | Hourly color temp for all lights |
| Front House Presence Dim | `fp2_front_house_off_after_5m_no_presence` | ON | Dim after no presence |
| 3D Print Complete Notification | `3d_printer_print_complete_notification` | ON | Notify Pixel 10 when print finishes |
| 3D Printer LED On | `3d_printer_led_strip_on` | ON | Turn on LED strip when print starts |
| 3D Printer LED Off | `3d_printer_led_strip_off` | ON | Turn off LED strip when print ends |
| Weekday Morning Lights | `weekday_morning_kitchen_dining_lights` | ON | Kitchen/dining 15% at 6:15 AM Mon-Fri |
| Mealie Shopping List Sync | `mealie_google_keep_shopping_list_sync` | ON | Sync Mealie → Google Keep every 20 min |

### Hourly Adaptive Temperature Automation

Runs every hour at `:00` with **2-minute transition**. Only affects lights that are **currently ON** - never turns on lights that are off. Preserves brightness.

**Color temp range:** 2700K (warm) to 5500K (daylight) - follows sun position via Adaptive Lighting integration.

**Lights covered (11 total):**
- **Front House:** living_room_color, kitchen_color, kitchen_color_1, dining_room_color_1, dining_room_color_2, extended_color_light_1
- **Master Bedroom:** hue_color_lamp_1, hue_color_lamp_1_2, hue_color_lamp_1_3
- **Toby's Room:** toby_s_room_color, toby_s_room_color_2

**Not included** (no color temp support): on_off_plug_1 (Printer), dimmable_light_1 (Toby's Lamp)

## Dashboard Patterns

The iPad dashboard uses custom:button-card templates. Key template: `room_card`

Variables supported:
- `color` - Card accent color
- `light_entity` / `light_entities` - Light to control
- `temp_entity` - Temperature sensor
- `door_entity` / `door_entity_2` - Door sensors
- `speaker_entity` - Media player

### Room Cards
- **Front House** - Controls `light.front_house`, uses indigo accent color (#6366f1)
- Other rooms: Living Room, Kitchen, Master Bedroom, Toby's Room, Outside

### Calendar View (`/Volumes/config/dashboards/views/calendar.yaml`)
Uses `custom:week-planner-card` (HACS) with toggle between Week and Month views.

**Week View (default):**
- 7 days starting Monday, `columns` forced to 7 at all breakpoints
- Weather icons via `weather.pirateweather`
- Navigation arrows to browse weeks
- Today: subtle warm tint (`#f9f7f4`) + green "Today" text (no borders, no circles)

**Month View:**
- 4 weeks (28 days) starting from current Monday — not a calendar month
- 7 columns forced at all breakpoints via `columns` config
- Navigation arrows to browse forward/back
- Same today styling as week view

**State model:** Both views use `input_select.calendar_view_mode` (options: `week`, `month`) with toggle scripts `script.toggle_week_view` / `script.toggle_month_view`. No fallback card needed — the input_select always has a valid state.

**Week-planner-card columns fix:** The sidebar layout narrows the content area below the card's responsive "large" breakpoint (1280px), causing it to fall to 5 columns. Fix: set `columns: { extraLarge: 7, large: 7, medium: 7, small: 7, extraSmall: 7 }` on both views. Additionally, `.container .day` needs `box-sizing: border-box` if custom `padding` is applied — otherwise padding adds to the width calculation and the 7th day wraps to the next line.

**Add Event popup:** Home Hub uses `calendar_event_popup_home_hub.yaml` (green palette) via `fire-dom-event` inline. Legacy iPad calendar uses `calendar_event_popup.yaml` (blue palette). The `open_calendar_event_popup` script resets form fields before opening — only used by the legacy calendar path.

## Home Hub Dashboard (New Sidebar Pattern)

Location: `/home-hub/*` views, config in `/Volumes/config/dashboards/home-hub/`

What we changed (Jan 18, 2026):
- Implemented a reliable collapsible sidebar using two static layouts per view (expanded 260px, collapsed 64px) instead of trying to resize one grid dynamically.
- Added a consistent 16px gap between sidebar and content to prevent shadow overlap.
- Extracted each view's main content into a decluttering template to avoid duplication.

What we changed (Jan 20, 2026):
- Fixed YAML structure corruption in `decluttering_templates.yaml`:
  - `home_hub_rooms_main` was missing its `cards:` array (content was orphaned at end of file)
  - `home_hub_calendar_main` was missing month view conditionals (they were in family_main)
  - `home_hub_family_main` had misplaced calendar and rooms content
- Narrowed sidebar from 260px to **198px** to better fit content
- Set weather widget width to **188px** to match nav items
- Changed nav item grid from `1fr` to `auto` so they don't expand unnecessarily

What we changed (Jan 21, 2026):
- Redesigned Rooms view to match mockup (see `/examples/mockup/rooms.png`)
- **Scene buttons**: Created new `home_hub_scene_chip` template - compact pill buttons with white background, gray border, neutral styling (replaces full-width colored buttons)
- **Room cards** (`home_hub_room_card` template) redesigned:
  - Layout: Name at top-left, temperature below, icon at bottom-left, light status at top-right
  - Card: 170px height, 24px border-radius
  - Title: 15px, font-weight 500 (medium, not bold)
  - Temperature: Uses `states[variables.temp_entity]` directly (button-card built-in), shows decimal (72.3°F)
  - Room icon: 56x64px rounded rectangle (#E0E7FF background), outline icons, blue (#4F6BED)
  - Light status: 40px circle, outline lightbulb icon, amber (#D97706) when on
- Updated all room icons to outline variants (`mdi:home-outline`, `mdi:sofa-outline`, etc.)
- Changed Rooms header to "Home"

What we changed (Jan 26, 2026):
- **Switched to Lucide icons** (inline SVGs) - no HACS integration needed
- **Room card icons updated** with per-room colors:
  - Front House: `home` (#488cd0 blue)
  - Living Room: `sofa` (#a386d7 purple)
  - Kitchen: `chef-hat` (#5aa287 green)
  - Bedroom: `bed` (#5aa287 green)
  - Toby's Room: `layers` (#f4b143 amber)
  - Outside: `cloud-sun-rain` (#549f82 teal)
- **Room card styling**:
  - Icon background: #f8f8f6
  - Temperature font color: #7c8493
  - Light icon (on): #f49f10 icon, #feebd6 background
  - Light icon (off): #D1D5DB icon, #F3F4F6 background
- **Outside card** now has door sensors (gate + shed) displayed as status icons
  - Gate: `door-closed-locked` (closed) / `door-open` (open)
  - Shed: `door-closed` (closed) / `door-open` (open)
  - Open state: red icon (#ef4444) on light red bg (#fee2e2)
  - Closed state: green icon (#22c55e) on light green bg (#dcfce7)
- **Status icons** (light, gate, shed) now vertically aligned in single column on right side of card
- **Scene chips** changed to icon-only circular buttons (44px, #f2f1ed background):
  - Relax: `moon`
  - All Off: `lightbulb-off`
  - Bright: `sun`
  - Morning: `sunrise`
  - Good Night: `moon-star`
- **Header template** changed to text-only (no icon, no button styling)
- **View background** changed to #fbfaf9
- **Card tap action**: Toggles light on/off; hold action opens popup with controls

What we changed (Feb 5, 2026):
- **Meals view**: Redesigned to match mockup with compact day pills, section headers, and recipe browser grid
- **Day pills** (`home_hub_meal_day_pill` template): Show day abbreviation, meal icon (green fork-knife if assigned, gray plus if empty), truncated meal name. Today highlighted in green (#4A7C59).
- **Recipe browser**: 3-column auto-fill grid of recipe cards from `sensor.mealie_recipe_browser`, each showing image placeholder, name, and cook time. Clicking opens recipe in Mealie.
- **Sidebar nav**: Added Meals item (`mdi:silverware-fork-knife`) to both expanded and collapsed sidebars
- **Mealplan serialization fix**: Transformed `mealie_fetch_mealplan` automation to output clean serializable dicts instead of raw Python objects (datetime.date, enums). Sensor now stores proper JSON-compatible list.
- **Mealplan date range fix**: Changed from "today + 6 days" to Mon-Sun of current week, matching the day pill layout
- **Recipe selector sync**: New `mealie_sync_recipe_selector` automation keeps `input_select.recipe_selector` options in sync with Mealie recipes on recipe update and HA start
- **Assign meal script**: Replaced duplicate hardcoded scripts with single dynamic version using `selectattr` lookup from sensor data
- **Width fix**: Added explicit `grid-template-areas` and `grid-template-columns: 1fr` to button-cards using only `custom_fields` (prevents grid collapse)

What we changed (Feb 22, 2026):
- **Fixed meal assignment date bug**: `assign_meal_to_day` script was calculating dates forward from today (`(target_dow - today_dow + 7) % 7`), causing past days (e.g., Monday when today is Friday) to assign to next week. Replaced with Monday-anchored calculation matching the mealplan fetch automation and day pill template.
- **Recipe detail popup**: Clicking a recipe card now opens a browser_mod popup (via `ll-custom` event dispatch) showing name, description, times, yield, and links to original source and Mealie. Previously opened Mealie URL directly (required login).
- **Recipe import popup**: "+ Add Recipe" button now opens a browser_mod popup with URL input instead of linking to Mealie's create page. Uses new `input_text.recipe_import_url` helper and `script.import_recipe_from_url` script.
- **Popup file**: `/Volumes/config/dashboards/popups/recipe_import_popup.yaml` (same Cancel/Action button pattern as `meal_selection_popup.yaml`)
- **Mealie password reset**: Reset via admin API (generate-token → reset-password flow). Username: `bennbennett`.

What we changed (Feb 23, 2026):
- **Meals view visual refinement**: Updated Home Hub Meals layout to better match mockup screenshots (`examples/home-hub-debugging/meals-mockup.png` vs `meals-actual.png`) including refined header scale, weekly dinners container, day chips, and recipe cards.
- **Recipe Browser controls**: Added/iterated functional search + category filters with metadata-aware classification fallback.
- **Popup click behavior fix**: Removed root card interaction conflicts so recipe cards, search input, and chips are clickable under Recipe Browser.
- **Clear assigned meal**: Added `script.clear_meal_for_day` and popup `Clear` button (`/Volumes/config/dashboards/popups/meal_selection_popup.yaml`), plus centered 3-button action row (`Cancel`, `Clear`, `Assign`).
- **Mealie clear sentinel flow**: `clear_meal_for_day` writes a sentinel note title (`__HA_CLEARED__`) via `mealie.set_mealplan`; `mealie_fetch_mealplan` maps sentinel to empty title so day pills render as unassigned (`+ Dinner`).

What we changed (Mar 1, 2026):
- **Weekly Grocery List Generator**: New CLI tool `tools/generate_grocery_list.py` reads the weekly meal plan from HA, creates/populates a "Weekly Groceries" shopping list in Mealie using native recipe-to-shopping-list endpoint. Supports `--preview`, `--sync` (Google Keep), and `--clear` flags.
- **Grocery list popup**: New `/Volumes/config/dashboards/popups/grocery_list_popup.yaml` with `todo-list` card for `todo.mealie_weekly_groceries` (built-in check/edit/delete) plus Close, Clear All, and Send to Keep action buttons.
- **Grocery List button on Meals view**: Added to Weekly Dinners section header in `decluttering_templates.yaml` — shopping cart icon with item count badge, opens grocery list popup via `browser_mod.popup`.
- **Entity name correction**: Mealie integration names the shopping list entity `todo.mealie_weekly_groceries` (not `todo.mealie_shopping_list`). Updated all references in `automations.yaml`, `meals.yaml` (tablet), popup, decluttering templates, and docs.

What we changed (Mar 1, 2026 - cont'd):
- **Recipe detail popup newline fix**: Fixed `openRecipePopup` in `decluttering_templates.yaml` — `'\\n\\n'` (double-escaped) produced literal `\n\n` text instead of actual line breaks. Changed to `'\n\n'` (single-escaped) so YAML passes real newline characters to JavaScript.
- **Removed duplicate heading**: Removed `## recipe.name` from popup markdown body since the popup title bar already displays the recipe name.
- **Recipe image in popup**: Added recipe image at the top of the popup using Mealie's media API (`/api/media/recipes/{recipe_id}/images/min-original.webp`). Only shown when `recipe.image` is truthy and not `'None'`. Images are served publicly (no auth needed). The `image` field (4-char hash) in sensor data indicates an image was set but doesn't guarantee the file exists on disk — recipes imported without images will simply skip the image.

What we changed (Mar 2, 2026):
- **Recipe Browser touch behavior**: Updated Home Hub Meals recipe cards and filter chips to use explicit pointer/touch handling so iPad taps reliably open popups and switch filters. Also disabled root card tap conflicts that interfered with touch input.
- **Button-card JS template fix**: Resolved `ButtonCardJSTemplateError: Identifier 'entity' has already been declared` by renaming the local grocery badge variable in `decluttering_templates.yaml`.
- **Grocery popup clear-all fix**: Replaced the popup's old `todo.remove_completed_items` action with `script.clear_weekly_groceries`, which fetches all `todo.mealie_weekly_groceries` items and removes them one by one. Reloaded HA scripts after adding the script.
- **Runtime automation alignment**: Reloaded HA automations after confirming the live automation still referenced stale entity `todo.mealie_shopping_list` even though config had already been updated to `todo.mealie_weekly_groceries`.
- **Manual Mealie recipe cleanup**: Deleted stuck recipes `test-import` and `test-import-1` directly from `/DATA/AppData/mealie/data/mealie.db` on the server after Mealie API/UI deletion failed with `ValidationError` caused by null ingredient `reference_id` values. Backup created at `/DATA/AppData/mealie/data/backups/mealie.db.20260301-145123.pre-delete-test-import.bak`.

What we changed (Mar 20, 2026):
- **Kiosk mode**: Installed `kiosk-mode` (manual install, not HACS) to hide HA header bar, tab bar, and sidebar on the Home Hub dashboard. JS file at `/www/kiosk-mode/kiosk-mode.js`, registered via `extra_module_url` in `configuration.yaml`. Dashboard config `kiosk_mode: kiosk: true` in `home-hub.yaml`. Append `?disable_km` to URL to temporarily show HA chrome. **Requires HA restart** to load the new `extra_module_url`.
- **NaN temperature guard**: Room cards now hide the temperature line entirely when sensor returns NaN, `unavailable`, or `unknown` (instead of showing "NaN°F"). Falls back to showing "Lights on"/"Lights off" status text.
- **Weather H:/L: guard**: Weather widget hides the high/low row when forecast data is missing (instead of showing "H: --° L: --°").
- **Scene chip labels restored**: Changed scene chips from icon-only 44px circles back to labeled pills matching the mockup — "Relax", "All Off", "Bright", "Morning", "Good Night". Each chip now takes a `chip_label` variable alongside `chip_icon`. White background with gray border, icon + label layout.
- **Light status fallback**: Room cards that lack a temperature sensor (or whose sensor is unavailable) now show "Lights on" (amber) or "Lights off" (gray) text below the room name, filling the previously empty middle area.
- **Unified filter chip styling**: Devices view filter pills updated from lighter green (#5aa287) to sage green primary (#4A7C59) with white border, matching the Meals view inline filter chips. Inactive state changed from beige (#f2f1ed) to white with gray border (#E5E7EB).

What we changed (Mar 20, 2026 - cont'd):
- **Fixed lightbulb icon alignment**: Room card status icons (lightbulb, door sensors) used `align-items: center` in the flex wrapper, which could shift icons away from the right edge depending on column width. Changed to `align-items: flex-end` to ensure consistent right-edge alignment matching `justify-self: end` on the grid cell.
- **Fixed weather widget justification**: Weather widget content was right-justified due to button-card's internal shadow DOM grid allocating slots for icon/state even with `show_icon: false`. Added `grid-template-areas: '"weather_content"'` to `styles.grid` to force a single-area layout, applying the same pattern documented in the "Button-card custom_fields width fix" memory. This resolves the long-standing known issue from Jan 20, 2026.

What we changed (Mar 25, 2026 — Calendar View Redesign):
- **State model fix**: Replaced 2 booleans (`input_boolean.calendar_week_view` + `calendar_month_view`) with single `input_select.calendar_view_mode` (options: week, month). Eliminated invalid "both off" state and removed fallback third planner card.
- **Header redesign**: Replaced 3 scene-button pills with layout-card grid row below header — Week/Month toggle pills + "+ Add Event" button. Matches Rooms view chip placement pattern (separate line below header, left-aligned).
- **Today styling**: Subtle warm tint (`#f9f7f4`) + green "Today" text only. Removed AI slop patterns (inset box-shadow left border, green circle on date number).
- **Add Event fix**: Changed from `call-service` to `script.open_calendar_event_popup` (which can't target the current browser for browser_mod.popup) to `fire-dom-event` with inline `browser_mod.popup` (proven pattern).
- **Green popup**: Created `calendar_event_popup_home_hub.yaml` with sage green palette matching Home Hub design. Legacy iPad calendar keeps original blue popup unchanged.
- **Month view**: Changed from `days: month` to `days: 28` (4 weeks from current Monday). More useful for planning than a calendar month that may start mid-week.
- **7-day grid fix**: Week-planner-card responsive breakpoints reduced columns to 5 when sidebar narrowed the content area. Fixed with explicit `columns` config forcing 7 at all breakpoints. Also fixed `box-sizing: border-box` on `.container .day` — padding added to width calculation caused the 7th day to wrap.

**Kiosk Mode:**
- **Install method:** Manual (downloaded JS from GitHub, not via HACS)
- **File:** `/Volumes/config/www/kiosk-mode/kiosk-mode.js`
- **Registration:** `frontend.extra_module_url` in `configuration.yaml` (global load)
- **Config:** `kiosk_mode: kiosk: true` in `home-hub.yaml` (per-dashboard)
- **Override:** Add `?disable_km` to any Home Hub URL to temporarily show HA chrome
- **Scope:** Only affects dashboards with `kiosk_mode` config — other dashboards unaffected
- **Requirement:** HA restart needed after adding to `extra_module_url`

**Mealie image URL pattern:** `http://100.68.225.20:9925/api/media/recipes/{recipe_id}/images/{size}` where size is `original.webp`, `min-original.webp` (recommended), or `tiny-original.webp`.

**Room card variables:**
- `room_name` - Display name (e.g., "Front House")
- `room_icon` - Lucide icon key (e.g., "home", "sofa", "chef-hat")
- `room_icon_color` - Icon stroke color (e.g., "#488cd0")
- `temp_entity` - Temperature sensor entity (falls back to light status text if unavailable)
- `light_entity` - Light entity for status indicator and toggle
- `door_entity` - Door sensor for gate (Outside card)
- `door_entity_2` - Door sensor for shed (Outside card)

**Scene chip variables:**
- `chip_icon` - Lucide icon key (e.g., "moon", "sun", "sunrise", "lightbulb-off", "moon-star")
- `chip_label` - Display label (e.g., "Relax", "All Off", "Bright", "Morning", "Good Night")

**Mockups location:** `/examples/mockup/` (rooms.png, calendar.png, devices.png, etc.)

What we changed (Apr 1, 2026):
- **Tasks & Lists view redesigned**: Two-column layout with Shopping List (`todo.google_keep_shopping_list`) and Family Todo (`todo.google_keep_family_todo`) using mushroom headers with "X active" counts and sage green accents. `hide_completed: false` shows both active and completed items.
- **Devices view popups**: Added styled popups for Pixel 10, Small iPad, Big iPad, and Printer (previously used default `more-info`). Each phone/tablet popup shows battery bar, network, Ring Device button, and footer. Printer popup shows 4 CMYK toner level bars. Fixed iPhone popup: replaced broken `script.find_iphone` with `script.ring_iphone`, removed Location section, removed Play Sound/Lock/Sync quick actions.
- **Ring Device scripts**: Created `script.ring_iphone`, `script.ring_pixel_10`, `script.ring_small_ipad`, `script.ring_big_ipad` in `scripts.yaml`. iOS uses critical notification with sound. Android uses alarm_stream channel.
- **groups.yaml**: Updated Garmin watch group to reference `script.ring_iphone` (was `script.find_iphone`).
- **Family view redesigned**: Gateway page simplified to 3 person cards with navigate actions (removed Location Overview map and Family Todo, which now lives on Tasks view). Header changed to "Family Members" with subtitle.
- **Family subpages**: All 3 family members get full subpages. Toby (`/home-hub/toby`) converted from old `max-content` sidebar to standard pattern, content moved to `home_hub_toby_main` decluttering template. Ben (`/home-hub/ben`) new page with Next Event + 3D Printer status + "Coming Soon" placeholders for Daily Wisdom, Todo, Commute, Health, Server Stats. Petra (`/home-hub/petra`) new page with Next Event + Weather + This Week's Meals + "Coming Soon" placeholders for Tide Times, Photography, Todo.
- **Background fix**: Fixed `#F9FAFB` → `#fbfaf9` on Tasks, Devices, and Family views to match other Home Hub views.
- **Skill routing**: Added `## Skill routing` section to CLAUDE.md for gstack skill auto-invocation.

Key files:
- Views: `/Volumes/config/dashboards/home-hub/views/*.yaml`
- Button card templates: `/Volumes/config/dashboards/home-hub/button_card_templates.yaml`
- Sidebars + decluttering templates: `/Volumes/config/dashboards/home-hub/decluttering_templates.yaml`
- Sidebars toggled by: `input_boolean.sidebar_collapsed`

Converted views (done): Rooms, Calendar, Tasks, Devices, Family, Meals, Toby, Ben, Petra
All views now use the standard sidebar pattern. No pending conversions.

What we changed (Apr 7, 2026 — Editorial Kitchen Redesign / `/critique` Phases 1-4):
This was a multi-phase, score-driven redesign launched after `/critique` graded the dashboard 18/40 ("Functional but unrefined"). Direction: **Editorial Kitchen** — warm-neutral palette + Fraunces serif + glance-first landing. Source of truth: `CRITIQUE-ACTION-PLAN.md` in repo root.

**Phase 1 — Cleanup (`/distill` + `/harden`):**
- Re-enabled kiosk mode (uncommented `kiosk_mode: kiosk: true` in `home-hub.yaml` AND `/local/kiosk-mode/kiosk-mode.js` in `configuration.yaml` `extra_module_url` — both were stale-commented).
- Deleted Coming Soon placeholders from Ben (5 cards) and Petra (3 cards) subpages.
- Tasks count headers fixed: `state_attr('todo.x', 'items')` returned empty (attr doesn't exist on those entities); changed to `states('todo.x')` which returns active count directly. Set `hide_completed: true` on both todo-list cards to stop the 4000px-tall page.
- Toby's `unavailable°F` literal text fixed via Jinja conditional showing "Sensor offline".
- Devices view: `mdi:tablet-ipad` icon doesn't render in this MDI version → replaced with `mdi:tablet`.
- Ben page Next Event fixed: switched from `calendar.home_calendar` to `calendar.ben_personal`.

**Phase 2 — Glance + Warmth (`/onboard` + `/bolder` + `/arrange`):**
- **Right Now landing page** (new default `/home-hub/right-now`, first view in `home-hub.yaml`): 132px Fraunces clock, Fraunces "Good evening, Bennetts" italic greeting, weather card, Tonight's Dinner card with terracotta icon, hourly forecast strip (HACS `lovelace-hourly-weather`), and a custom upcoming events list grouped by day with TODAY/TOMORROW/Weekday eyebrows.
- **New entities**: `sensor.live_time`, `sensor.live_date_long`, `sensor.live_greeting` (30s `time_pattern` triggered template sensors in `configuration.yaml`); `sensor.home_hub_upcoming_events` (event-triggered template sensor populated by `home_hub_fetch_upcoming_events` automation that runs every 5 min calling `calendar.get_events` on home_calendar + ben_personal + work_calendar + birthdays_anniversaries).
- **Family page redesign**: Replaced thin broken person cards (which referenced non-existent `person.toby`/`person.ben`/`person.petra`) with rich `home_hub_person_card` template — avatar circle, Fraunces serif name, UP NEXT block from filtered calendar. Per user feedback, the cards do NOT show home/away presence or phone battery (Bennetts know where each other are; battery isn't actionable). Each person filters by their primary calendar:
  - Ben → `calendar.work_calendar` (his actual driver) + Outlook all-day normalization
  - Petra → `calendar.home_calendar` (no personal HA calendar)
  - Toby → `calendar.home_calendar` (no calendar — he's 10)
- **Outlook all-day normalization**: Outlook (`work_calendar`) returns multi-day events as midnight-to-midnight TIMED events (not `all_day: True` like Google Calendar). The events automation now detects `'T00:00:00' in start_raw and end_raw` and normalizes them to `all_day: True` with YYYY-MM-DD start/end. Without this, "Out of office" displayed as "Thu · 12:00 AM" instead of "Through Apr 13".
- **Multi-day event grouping**: Right Now agenda groups currently-active multi-day all-day events under TODAY (instead of their original start date) with "Until [day]" labels.
- **Sidebar reorder**: Home (right-now landing) → Calendar → Tasks → Meals → Rooms (new — was "Home") → Devices → Family. "Home" now means the glance landing; Rooms is its own item.

**Phase 3 — Visual Identity (`/typeset` + `/colorize` + `/clarify` + `/delight`):**
- **Fraunces serif** (`/typeset`): Created `/Volumes/config/www/home-hub-fonts.js` that injects Google Fonts Fraunces (variable, opsz 9..144, weights 300-700) into the document head. Registered in `frontend.extra_module_url` as `/local/home-hub-fonts.js`. Applied to: all `home_hub_header` page titles (34px), Right Now hero greeting/AM-PM/date, Tonight's Dinner meal name, Coming Up agenda eyebrow, Room card titles, Person card display names, "Plan this week" Meals header, "Weekly dinners" + "Recipe browser" subheaders, Calendar header. Body and dense data stay system sans for legibility.
- **Two-color discipline** (`/colorize`): Sage `#4A7C59` reserved for ACTION (buttons, nav, primary state); terracotta `#C87456` introduced for "current moment" (TODAY, TONIGHT, UP NEXT, today's day pill, calendar Today text). New tokens: `#FFF6F1` (terracotta tint), `#FCE9DE` (terracotta peach for active press / today badges).
- **Friendlier copy** (`/clarify`): Removed "Family Members / Select a family member" robot subtitle. Person card empty states use friendly fallbacks ("No work events" / "A quiet day at home") instead of "Nothing scheduled". Date display shows "Apr 14 · 2:00 PM" instead of "Tue · 2:00 PM" for events more than 6 days out. Meals banner copy now reads "Pick this week's dinners from the recipes below ↓" (empty), "N more to go for the week" (partial), "Week's planned. Time to make the grocery list →" (full).
- **Sidebar weather "Partlycloudy" bug fixed**: `home_hub_weather_expanded` template's condition formatter only handled dashed conditions; added explicit condMap so "partlycloudy" → "Partly cloudy".
- **Animation moments** (`/delight`): Added `hh-pulse` and `hh-fade-in` keyframes globally via `home-hub-fonts.js` (with `prefers-reduced-motion` override). Person cards and room cards lift on hover (`translateY(-3px)` + softer shadow, `cubic-bezier(0.2, 0.9, 0.3, 1.2)` ease). Press feedback on `:active` (translateY(-1px) + scale(0.99)). Scene chips warm to terracotta on hover, snap-press on tap. Right Now's "TODAY" eyebrow has a 6px terracotta dot that pulses every 2.4s — drawing the eye without being demanding.

**`button-card` reserved variables (memory)**: Don't use `html` OR `hass` as local variable names in JS templates — both conflict with built-ins and produce `Identifier 'X' has already been declared`. Use `output`, `result`, `haObj`, etc.

**Live YAML reload trick (memory)**: For YAML-mode dashboards (`home-hub`), HA caches the parsed config. Force a hot-reload via the WebSocket trick `ha.hass.connection.sendMessagePromise({type: 'lovelace/config', url_path: 'home-hub', force: true})` instead of restarting HA. Useful for fast Playwright edit-verify loops. HA restart is the bulletproof fallback if the trick doesn't take.

What we changed (Apr 7, 2026 cont'd — Phase 5: Coherence pass / `/clarify` + `/colorize`):
After the Phase 1-4 redesign landed at 24/40, `/critique` flagged two P0 issues that broke the editorial direction even though everything else was working: (1) the calendar's repeating multi-day events, (2) the leftover Material-UI icon palette on Rooms/Devices/Family that didn't sit in the warm Editorial Kitchen system. Phase 5 fixed both.

**Calendar refactor (`/clarify`):**
- **Multi-day event repetition fixed.** Set `multiDayMode: single` on `custom:week-planner-card` (week + month views). "ben - spring break" was rendering as 7 identical "Entire day" pills across the row → now appears once on its start day. Same for "Toby spring break" (was 5+ cells → 1).
- **week-planner-card v1.14.1 config bug**: the card source reads `e._multiDayTimeFormat` (with underscore prefix) instead of `e.multiDayTimeFormat` for the multi-day time format key. Set the YAML config key WITH the leading underscore — `_multiDayTimeFormat: "MMM d"` — to actually apply the format. Documented inline in `decluttering_templates.yaml` so it doesn't get reverted.
- **12-hour AM/PM format everywhere.** Calendar week + month views now use `timeFormat: "h:mm a"` to match the Right Now clock and hourly forecast. "17:25 - 17:55" → "5:25 PM - 5:55 PM".
- **"Entire day" prefix dropped** via `texts.fullDay: " "` override.
- **Quieted time metadata.** Times in week + month views now render as small uppercase gray (`text-transform: uppercase, font-size: 10px, color: #9CA3AF`) so the title gets visual priority.
- **Title clamping.** `-webkit-line-clamp: 2` truncates long titles cleanly instead of pushing cells to absurd heights.
- **Day labels reformed.** Dropped the redundant relative labels ("Yesterday", "Tomorrow", "Thursday", "Friday") via `.container .day .date .text { display: none; }`. Today gets a single dedicated `TODAY` terracotta eyebrow under the number via `::after` pseudo-element. One source of "now" signaling instead of two.
- **Right Now agenda — present-tense labels.** "Until Mon" → "Through Mon" in `home_hub_right_now_main`.
- **Right Now agenda — raw bullet stripping.** Calendar event titles like `"Stay at Misty Mountain Chalet- Pets•EV•Trails•Views•2acres"` (Outlook metadata leak) now strip to `"Stay at Misty Mountain Chalet"`. Regex matches a dash-prefixed segment with bullet runs only — leaves normal titles like `"ben - spring break"` intact.
- **Right Now agenda — title overflow.** Added `white-space: nowrap; overflow: hidden; text-overflow: ellipsis` to the title cell so long titles ellipsis-truncate cleanly.

**Icon palette unification (`/colorize`):**
Committed to a 6-color editorial palette where every color sits in the warm spectrum (no blues/purples/teals). The 6 colors all read as siblings from the same paint chip set, low-saturation warm-earth family.

| Slot | Hex | Use |
|---|---|---|
| Sage | `#4A7C59` | Living Room, batteries, tablets, system primary action |
| Terracotta | `#C87456` | Front House, phones, birthdays, Petra avatar, "current moment" |
| Honey | `#B89254` | Kitchen, both printers (food/appliance warmth) |
| Taupe | `#8E7065` | Bedroom, work_calendar dot |
| Clay | `#9A6B47` | Toby's Room, Toby avatar, Toby school tile |
| Olive | `#6E8E4D` | Outside, ben_personal calendar dot |
| Dusk indigo | `#3D3654` | Hourly forecast night blocks (was harsh `#111`) |

Touched:
- **Room cards (6):** retinted Front House (was `#488cd0` blue → terracotta), Living Room (`#a386d7` purple → sage), Kitchen (`#5aa287` green → honey), Bedroom (`#5aa287` → taupe), Toby's Room (`#f4b143` → clay), Outside (`#549f82` → olive). All popup `mushroom-title-card` border-left accent colors updated to match.
- **Tinted tile backgrounds.** The room icon tile derives its background from the room color at 14% alpha (`rgba(r, g, b, 0.14)`) instead of being a uniform `#f8f8f6`. Each room gets its own warm tile, and the icon stays legible without fighting low-contrast strokes. Icon bumped to 28px with stroke-width 2.25 for stronger presence.
- **Device cards (6):** phones (iPhone, Pixel 10) → terracotta, tablets (Small iPad, Big iPad) → sage, both printers (Brother + Centauri Carbon) → honey, batteries → sage. Default `device_color` fallback in `home_hub_device_card` template also updated from `#a386d7` purple to `#4A7C59` sage.
- **Family avatars:** Ben already sage, Petra already terracotta — Toby switched from blue `#3B82F6` to clay `#9A6B47` (matches his room and his school tile).
- **Toby's Corner — School tile:** clay tile + clay icon (was blue). Other tiles (Swimming/Hockey/I'm Bored) intentionally kept their semantic colors — water=cyan, hockey=red, play=orange — kid-friendly is a feature.
- **Right Now agenda calendar dots:** updated `calColors` map — `home_calendar` stays sage, `birthdays_anniversaries` already terracotta, `ben_personal` blue → olive, `work_calendar` purple → taupe.
- **Calendar week + month views:** `birthdays_anniversaries` calendar color in week-planner-card config changed from purple `#9333EA` to terracotta `#C87456`. Legend dot reflects this.

**Hourly forecast night-block fix (the gnarly one):**
The `lovelace-hourly-weather` card defines its color variables on a `.main` selector inside `weather-bar`'s nested shadow root. card-mod can't reach into nested shadow roots from the parent — even setting the variable on the `weather-bar` host element with `!important` was overridden by the internal `.main` declaration. Solution: added a JS patcher to `home-hub-fonts.js` that walks the DOM, finds every `weather-bar` element, and injects a `<style>` tag directly into its shadow root with the warm overrides (clear-night → `#3D3654`, cloudy → `#B6B0A2`, partlycloudy → `#C6D8E8`, sunny → `#F5C57F`, plus matching foregrounds). Runs on script load + every 1.5s via `setInterval` to catch newly mounted weather-bar elements (e.g. when the hourly card re-renders).

**Required for iPad pickup**: the new `home-hub-fonts.js` (with the night-block patcher) is browser-cached on the iPad. Either hard refresh once on the iPad (Safari → close tab → reopen), or restart HA so `extra_module_url` re-busts. Without that, the iPad keeps showing black night blocks even though the patch is shipped to disk.

**New memory entries**:
- **week-planner-card `_multiDayTimeFormat` underscore bug** (v1.14.1): config key requires underscore prefix to be read.
- **Nested shadow root CSS variables**: `lovelace-hourly-weather`'s color vars live on `.main` inside `weather-bar`'s nested shadow root, not on `:host`. card-mod can't reach them — must inject `<style>` directly into that shadow root via JS.
- **Tinted tile background pattern**: derive icon tile background from `rgba(r, g, b, 0.14)` of the icon color so each card gets its own warm tile and icons stay legible.

What we changed (Apr 4, 2026 — Design Unification + Mealie Fix):
- **Mealie shopping list auto-sync removed**: Removed 20-minute `time_pattern` trigger from `mealie_google_keep_shopping_list_sync` automation. Sync now only fires when user explicitly presses "Send to Keep" via `input_button.sync_shopping_list`. This fixes the bug where clearing Google Keep items would be undone within 20 minutes by stale Mealie list items being re-synced.
- **Unified design language across all Home Hub views**: Standardized card styling tokens so every page shares the same visual treatment:
  - **Card border-radius**: Room cards `24px` → `16px`, Device cards `12px` → `16px`. All content cards now `16px`.
  - **Card elevation**: All cards now use `box-shadow: 0 1px 3px rgba(0,0,0,0.05)` + `border: 1px solid #F3F4F6`. Removed `0.08` and `0.1` shadow variants. Added missing borders to room cards, person cards, calendar planner, and Toby room controls.
  - **Card padding**: Device cards `24px` → `20px`, Toby checklist cards `24px` → `20px`. All content cards now `20px`.
  - **Filter/chip pills**: Device filter pills standardized to match Calendar/Rooms: `border-radius: 22px`, `height: 40px`, `padding: 0 16px`, `font-weight: 500`, grid gap `8px`.
  - **Popup accent bars**: Added missing accent bars to Bedroom (green `#5aa287`) and Outside (teal `#549f82`) popups.
  - **Design system comment**: Fixed background color reference from `#F9FAFB` to `#fbfaf9` in `button_card_templates.yaml`.
- **HTML mockup**: Created `examples/mockup/home-hub-unified.html` — interactive mockup of all 6 views showing the unified design language. Switchable via bottom tab bar or sidebar nav.

**Standardized Design Tokens (Home Hub):**
| Token | Value |
|-------|-------|
| Page background | `#fbfaf9` |
| Card background | `#FFFFFF` |
| Card border-radius | `16px` |
| Card border | `1px solid #F3F4F6` |
| Card shadow | `0 1px 3px rgba(0,0,0,0.05)` |
| Card padding | `20px` (content cards) |
| Pill border-radius | `22px` |
| Pill height | `40px` |
| Pill font-weight | `500` |
| Pill grid gap | `8px` |
| Text primary | `#1F2937` |
| Text secondary | `#6B7280` |
| Text muted | `#9CA3AF` |
| **Sage primary** | `#4A7C59` (action color: buttons, nav, primary state, Living Room, batteries, tablets) |
| Sage light | `#E8F0EA` |
| **Terracotta accent** | `#C87456` ("current moment" — TODAY/TONIGHT/UP NEXT — and Front House, phones, birthdays, Petra avatar) |
| **Terracotta tint** | `#FFF6F1` (active scene chips, today day-pill bg) |
| **Terracotta peach** | `#FCE9DE` (today badges, dinner card icon bg, active press) |
| **Honey** | `#B89254` (Phase 5: Kitchen, Brother printer, Centauri Carbon — food/appliance warmth) |
| **Taupe** | `#8E7065` (Phase 5: Bedroom, work_calendar dot — calm) |
| **Clay** | `#9A6B47` (Phase 5: Toby's Room, Toby avatar, Toby school tile — kid-warm identity) |
| **Olive** | `#6E8E4D` (Phase 5: Outside, ben_personal calendar — earth/garden) |
| **Dusk indigo** | `#3D3654` (Phase 5: hourly forecast night blocks, replaces harsh `#111`) |
| Subtle border | `#E5E7EB` (pills, dividers) |
| Card border | `#F3F4F6` (card edges) |
| **Display font** | `Fraunces` serif (variable, opsz 9..144, weights 300-700) — page headers, hero text, person names, room titles |
| **Body font** | system-sans (legibility for dense data) |

**Room icon palette** (one-line lookup): Front House → terracotta, Living Room → sage, Kitchen → honey, Bedroom → taupe, Toby's Room → clay, Outside → olive. Each room card derives its tile background from the icon color at 14% alpha.

Pattern per view (panel view):
```
type: panel
cards:
  - type: vertical-stack
    cards:
      - conditional → layout-card (grid: 198px 1fr, gap 16px) → [sidebar_expanded, <view>_main]
      - conditional → layout-card (grid: 64px 1fr, gap 16px) → [sidebar_collapsed, <view>_main]
```

Notes:
- Always keep a single top-level card in panel mode (use a `vertical-stack`).
- Pin main content to column 2 via `view_layout` in the decluttering template.
- For calendar popups, use absolute includes (e.g., `/config/dashboards/popups/calendar_event_popup.yaml`).

Troubleshooting:
- Calendar view uses `input_select.calendar_view_mode` (week/month). Since it's an input_select (not two booleans), there's no invalid "both off" state — no fallback card needed.
- If Rooms view shows "Invalid configuration" error, check that `home_hub_rooms_main` template has a `cards:` array (YAML structure issue).
- **ButtonCardJSTemplateError: Identifier 'html' has already been declared** - Don't use `html` as a variable name in button-card JavaScript templates. It conflicts with button-card's built-in `html` template helper. Use `output`, `result`, or another name instead.
- **Recipe Browser area not clickable / default entity popup opens on click** - If using a `custom:button-card` as a JS-rendered container, avoid root card entity tap behavior intercepting child controls. Remove root `entity` binding for the container card (or ensure root actions do not capture click events), and read data from `states['sensor.*']` inside JS.
- **Trigger-based sensor attributes are strings instead of lists** - If a Mealie (or other integration) service call returns Python objects with non-JSON-serializable types (e.g., `datetime.date`, enums), passing them directly through `{{ variable }}` in event_data produces a Python repr string that HA can't parse back. Fix: transform to flat dicts with only string/number values in the automation before firing the event.

## The Countertop Dashboard (Kitchen Fridge iPad)

Location: `/the-countertop/*` views, config in `/Volumes/config/dashboards/countertop/`

What we built (Apr 9-10, 2026):
- **New kitchen fridge iPad dashboard** with hub-and-spoke navigation (5 views, max depth 1)
- Design brief at `DESIGN-BRIEF.md`, mockup at `mockup-countertop.html` (scored 31/40)
- Built in 7 stages after a failed first attempt that tried to do everything at once

**Architecture (different from Home Hub):**
- No sidebar — hub-and-spoke from Home screen
- Persistent scene bar on every view via `layout-card` with `grid-template-rows: 1fr auto`
- `type: panel` views with `custom:layout-card` as outer container
- Button card templates with SVGs defined inside JS (icon-key maps, never YAML variables)
- Scene bar included via `!include ../scene_bar.yaml` (relative from views/ dir)
- Dashboard key requires hyphen: `the-countertop` (HA validation rule)

**Views:**
| Path | Content |
|------|---------|
| `/the-countertop/home` | Clock, 3x2 action grid, agenda, dinner pool, secondary nav |
| `/the-countertop/lights` | 3x2 room cards (toggle + hold for controls) |
| `/the-countertop/calendar` | Week/month toggle, week-planner-card |
| `/the-countertop/toby` | School + Swimming checklists, I'm Bored randomizer |
| `/the-countertop/meals` | Dinner pool cards, recipe browser |

**New entities:**
| Entity | Purpose |
|--------|---------|
| `timer.kitchen_timer` | Kitchen timer with popup disc display |
| `input_text.add_to_list_item` | Shopping list quick-add input |
| `input_text.toby_new_activity` | "Add a new activity" text input on Toby's Corner |
| `input_select.toby_activity_selector` | Stores Toby's activity pool (options are dynamic) |
| `input_boolean.season_school` | Toggle School checklist visibility (Manage popup) |
| `input_boolean.season_swimming` | Toggle Swimming checklist visibility |
| `input_boolean.season_hockey` | Toggle Hockey checklist visibility |

**New scripts:**
| Script | Purpose |
|--------|---------|
| `script.ct_add_to_shopping_list` | Adds item to Google Keep, clears input |
| `script.toby_add_activity` | Adds new activity from input_text to activity_selector options |
| `script.toby_random_activity` | Picks random activity from input_select options (updated to read dynamically) |

**Key files:**
| File | Purpose |
|------|---------|
| `/Volumes/config/dashboards/countertop.yaml` | Main dashboard (kiosk, resources, views) |
| `/Volumes/config/dashboards/countertop/button_card_templates.yaml` | 4 templates (scene_chip, action_btn, room_card, checklist_card) |
| `/Volumes/config/dashboards/countertop/scene_bar.yaml` | Shared bottom bar (5 scene chips) |
| `/Volumes/config/dashboards/countertop/views/*.yaml` | 5 view files |

**Implementation lessons (avoid repeating):**
- Never pass SVG markup as YAML variables — it gets HTML-escaped. Use icon-key maps in JS.
- `!include` paths in view files resolve relative to the view file's directory, not the dashboard root.
- YAML list variables in button-card cause "Configuration error" — use comma-separated strings, split in JS.
- `position: fixed` CSS on cards is fragile — use layout-card grid rows instead.
- `ll-custom` event dispatch for service calls is unreliable — use separate button-cards with `tap_action: call-service`.
- HA dashboard URL keys must contain a hyphen (`the-countertop`, not `countertop`).

What we changed (Apr 10, 2026 — Phase 2: iPad Visual Fidelity):
- **Scene bar chips**: Full-width stretched → compact centered pills using dual-spacer pattern (`1fr repeat(5, auto) 1fr`). Padding fixed from `10px 24px` → `0 24px`.
- **Calendar controls**: Replaced `horizontal-stack` (forces equal width) with `layout-card` grid (`repeat(3, auto) 1fr auto`). Added missing "+ Add Event" button, right-aligned.
- **Secondary nav links**: Replaced inert HTML divs with 3 separate navigable button-cards in a layout-card grid.
- **Agenda + dinner pool tap actions**: Changed from `tap_action: none` to navigate to Calendar/Meals respectively.
- **Action button height**: `min-height` bumped from `110px` → `140px` to match mockup proportions on iPad 6th gen (1024x768 viewport).
- **Home grid right panel**: Narrowed from `320px` → `300px` to give action grid more room at 1024px.
- **Card borders**: `#F0EDE8` → `#E8E4DE` (slightly darker, visible on iPad at arm's length).
- **Calendar max-height**: Added `max-height: calc(100vh - 210px)` + `overflow-y: auto` + `compact: true` on week-planner-card so scene bar stays visible on iPad.
- **Recipe text sizing**: Name `13px` → `14px`, time `11px` → `12px`, image area `72px` → `80px` for arm's-length readability.
- **Vertical centering (Lights + Toby)**: JS patcher in `home-hub-fonts.js` sets `height: fit-content` + `alignSelf: center` on the vertical-stack inside `grid-layout`'s shadow root. card_mod can't reach nested shadow roots — JS patching is the only way.
- **Find Phone toast**: `browser_mod.sequence` calls ring script then shows terracotta popup ("Ringing Petra's phone...") with 3s timeout.
- **Shopping list popup**: Redesigned with inline input+Add layout and "View full list →" link.
- **Toby's Corner**: Added MANAGE button (same line as CHECKLISTS label, opens season toggle popup), Add Activity input+button, dynamic activity list from `input_select`.
- **Recipe browser serialization fix**: Namespace loop in `mealie_fetch_recipes` automation to transform Python repr string → clean dicts with string-only values. Same pattern as mealplan fix.

**iPad cache-busting for JS files:**
When updating `home-hub-fonts.js`, bump the `?v=N` query parameter on the URL in `configuration.yaml` `extra_module_url` (e.g., `?v=2` → `?v=3`), then restart HA. The companion app's WKWebView caches aggressively — `command_clear_cache` notification alone is NOT reliable. The `?v=N` URL change is the bulletproof approach.

What we changed (Apr 10, 2026 — Phase 3: Final Polish):
Three rounds of second-opinion review (Codex) drove the remaining gap from "functional but HA-looking" to "feels like part of the dashboard." The biggest wins were replacing HA's native input field chrome via JS shadow DOM patching, upgrading checklist popups from entities-card toggles to custom packing-list rows, and removing the modal overlay from Find Phone.

- **Checklist popup redesign**: Replaced `type: entities` toggle switches with `ct_checklist_item` button-card template. Each row: left-side 22px SVG checkbox (green/blue fill when checked, gray outline when unchecked), 36x36 tinted icon tile (16-key SVG map: apple, lunch, water, jacket, notebook, laptop, pencil, bag, shirt, swim, goggles, towel, sun, droplet, shorts), 15px label. Strikethrough + muted colors when checked. 56px row height, 8px horizontal padding, warm dividers (#F0EFED).
- **All popup chrome cleaned up**: Every popup (shopping, timer, phone toast, both checklists) now has `popup_styles` hiding `ha-dialog-header` and setting `--ha-dialog-border-radius: 24px`. Popup titles rendered as Fraunces serif inside the content instead of the HA dialog header.
- **Timer popup state fix**: Pause/Cancel row wrapped in `type: conditional` with `state_not: idle` — idle state shows only preset buttons. Added `size: narrow`.
- **Meals fixed 7-day layout**: Replaced dynamic-count grid with Mon-Sun slots. Each slot shows the assigned meal with day label badge, or a dashed placeholder ("Add Meal" + day abbreviation). Today's empty slot gets terracotta dashing and tint. Grid always stable regardless of how many meals are assigned.
- **Room card subtitle removal**: Removed "Lights off" fallback text from `ct_room_card` `rm_temp` field. Returns empty 13px spacer instead — the lightbulb icon already conveys on/off state.
- **Toby add-activity visual merge**: Bored card gets `border-radius: 16px 16px 0 0` with no bottom border. Add activity row gets `card_mod` with `0 0 16px 16px` bottom radius, matching white background, no top border. Reads as one continuous card.
- **Action button height**: `min-height` bumped from `140px` → `200px` in `ct_action_btn` to fill more vertical space on the iPad.
- **Swimming progress bar**: Hardcoded `#4A7C59` sage changed to `${color}` variable so it uses the card's `checklist_color` (blue for Swimming).
- **Calendar cleanup**: Hidden legend and weather on week view, set `compact: false` to give day cards more breathing room. Month view legend also hidden.
- **JS input patcher** (`patchInputFields()` in `home-hub-fonts.js`): New shadow DOM patcher that finds all `hui-input-text-entity-row` elements (including inside browser_mod popup shadow roots), hides the `state-badge` leading icon, and injects a `<style>` into each `ha-textfield` shadow root. Patches: hides `.mdc-line-ripple` (underline), `.mdc-floating-label`, `.mdc-notched-outline`; adds `border: 1px solid #E8E4DE`, `border-radius: 12px`, `height: 44px`; terracotta focus ring (`border-color: #C87456`). Route-gated to `/the-countertop`, runs every 1500ms. Handles both inline inputs (Toby page) and popup inputs (Shopping List dialog).
- **Find Phone transparent scrim**: Added `--mdc-dialog-scrim-color: transparent` to popup_styles — removes the screen-dimming modal overlay. Added `hh-fade-in` animation and light shadow for a toast-like feel.
- **Cache bust**: `?v=2` → `?v=3` on `extra_module_url` in `configuration.yaml`. HA restart required.

**New template:** `ct_checklist_item` in `/Volumes/config/dashboards/countertop/button_card_templates.yaml`
- Variables: `item_name` (string), `item_icon` (key into SVG map), `item_color` (hex)
- Entity: the `input_boolean` for this checklist item
- Tap action: toggle
- Icon map keys: apple, lunch, water, jacket, notebook, laptop, pencil, bag, shirt, swim, goggles, towel, sun, droplet, shorts

**JS patcher pattern (input fields):**
Uses the recursive `findAll` walker (like `patchHourlyWeather`, not the explicit-chain walker). Required because popup inputs live inside `browser-mod-popup` elements appended to `document.body` outside the normal HA shadow DOM tree. Deduplication via `data-ct-input` attribute on injected style tags.

## Troubleshooting

### API Returns Empty / JSON Parse Errors
Large API responses (like `/api/states` with 500+ entities) fail when piped directly to Python due to buffering issues. **Always save to a temp file first:**
```bash
# WRONG - will fail with "Expecting value" JSON error:
. .env && curl -s -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/states" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))"

# CORRECT - save to file first:
. .env && curl -s -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/states" > /tmp/ha_states.json
python3 -c "import json; print(len(json.load(open('/tmp/ha_states.json'))))"
```

Small responses (single entity, `/api/` test endpoint) can be piped directly.

### Samba Not Mounted
```bash
# Check mount
ls /Volumes/config/ 2>/dev/null || echo "Not mounted"

# Mount (same URL home and remote — Tailscale subnet route via bennett-server when away)
open "smb://192.168.68.114/config"

# If remote and this fails: verify Tailscale is connected and accept-routes is on
#   tailscale status | grep bennett-server
#   tailscale debug prefs | grep -i routeall   # should be: true
```

User must authenticate the Samba dialog when it appears.

### Token Expired (401 Error)
1. Go to HA web UI > Profile > Long-Lived Access Tokens
2. Create new token
3. Update `.env` with new HASS_TOKEN value

## Skill routing

When the user's request matches an available skill, ALWAYS invoke it using the Skill
tool as your FIRST action. Do NOT answer directly, do NOT use other tools first.
The skill has specialized workflows that produce better results than ad-hoc answers.

Key routing rules:
- Product ideas, "is this worth building", brainstorming → invoke office-hours
- Bugs, errors, "why is this broken", 500 errors → invoke investigate
- Ship, deploy, push, create PR → invoke ship
- QA, test the site, find bugs → invoke qa
- Code review, check my diff → invoke review
- Update docs after shipping → invoke document-release
- Weekly retro → invoke retro
- Design system, brand → invoke design-consultation
- Visual audit, design polish → invoke design-review
- Architecture review → invoke plan-eng-review
- Save progress, checkpoint, resume → invoke checkpoint
- Code quality, health check → invoke health

## For More Information

See `docs/INDEX.md` for detailed documentation on specific topics.
