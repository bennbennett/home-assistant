# Home Assistant Changelog

All notable changes to the Home Assistant configuration.

## [March 2, 2026]

### Fixed
- **Home Hub Meals touch interactions** (`/Volumes/config/dashboards/home-hub/decluttering_templates.yaml`)
  - Recipe cards now use explicit pointer/touch handling instead of relying on plain click behavior
  - Category filter chips, including `All`, now respond reliably on iPad/touch devices
  - Root card tap conflicts were removed so nested controls can receive touch events cleanly

- **Button-card JS template collision** (`/Volumes/config/dashboards/home-hub/decluttering_templates.yaml`)
  - Resolved `ButtonCardJSTemplateError: Identifier 'entity' has already been declared`
  - Renamed a local grocery badge variable that collided with button-card's built-in `entity`

- **Grocery popup clear-all behavior** (`/Volumes/config/dashboards/popups/grocery_list_popup.yaml`, `scripts.yaml`)
  - `Clear All` no longer uses `todo.remove_completed_items`
  - Added `script.clear_weekly_groceries` to remove all items from `todo.mealie_weekly_groceries`, including active items
  - Reloaded Home Assistant scripts after adding the new script

- **Stale Mealie shopping-list automation runtime**
  - Reloaded automations after confirming the live automation still referenced `todo.mealie_shopping_list`
  - Runtime now matches the corrected config that uses `todo.mealie_weekly_groceries`

### Changed
- **Broken Mealie test recipes removed from server data store**
  - Deleted `test-import` and `test-import-1` directly from `/DATA/AppData/mealie/data/mealie.db` after UI/API deletion failed
  - Root cause was malformed ingredient rows with null `reference_id`, which caused Mealie `ValidationError` responses on recipe load/delete
  - Cleaned linked ingredient, instruction, nutrition, settings, and timeline rows, and removed the leftover empty recipe directories
  - Backup created first: `/DATA/AppData/mealie/data/backups/mealie.db.20260301-145123.pre-delete-test-import.bak`

## [February 23, 2026]

### Changed
- **Home Hub Meals View: Mockup Refinement** (`dashboards/home-hub/decluttering_templates.yaml`, `dashboards/home-hub/button_card_templates.yaml`)
  - Refined visual hierarchy to better match target mockup (header scale, weekly dinners container, day-pill styling, recipe card density/tags)
  - Added functional Recipe Browser controls: text search + category chips (`All`, `Chicken`, `Beef`, `Seafood`, `Pork`, `Vegetarian`)
  - Added metadata-aware category mapping with keyword fallback for current payloads

### Fixed
- **ButtonCard JS template collision** (`dashboards/home-hub/decluttering_templates.yaml`)
  - Resolved `ButtonCardJSTemplateError: Identifier 'html' has already been declared`
  - Renamed local JS variable to avoid conflict with button-card built-in helper

- **Recipe Browser click interception** (`dashboards/home-hub/decluttering_templates.yaml`)
  - Root browser card no longer opens default HA entity popup
  - Recipe cards, search input, and filter chips are clickable as intended

- **Meal selection popup action layout** (`dashboards/popups/meal_selection_popup.yaml`)
  - Aligned `Cancel`, `Clear`, and `Assign` buttons on one centered row

- **Clear day workflow for assigned meals** (`scripts.yaml`, `automations.yaml`)
  - Added `script.clear_meal_for_day`
  - Uses `mealie.set_mealplan` with sentinel note (`__HA_CLEARED__`) to clear dinner entry
  - `mealie_fetch_mealplan` automation now filters sentinel titles to empty so UI shows `+ Dinner`

## [February 22, 2026]

### Fixed
- **Meal Assignment Date Bug** (`scripts.yaml`)
  - `assign_meal_to_day` script calculated dates forward from today: `(target_dow - today_dow + 7) % 7`
  - If today was Friday and user picked Monday, it assigned to **next** Monday — outside the current week's view range
  - Replaced with Monday-anchored calculation: compute current week's Monday, then add target day-of-week offset
  - Now matches how `mealie_fetch_mealplan` automation and day pill template calculate dates

### Added
- **Recipe Detail Popup** (Home Hub Meals view)
  - Clicking a recipe card now opens a `browser_mod.popup` inside HA instead of navigating to Mealie
  - Popup shows: recipe name, description, prep/cook/total time, yield, original source link, and Mealie link
  - Uses `ll-custom` event dispatch from button-card JS template
  - Recipe names/descriptions are HTML-entity-escaped to prevent injection

- **Recipe Import from URL** (Home Hub Meals view)
  - "+ Add Recipe" button now opens an import popup instead of linking to Mealie's create page
  - New helper: `input_text.recipe_import_url` (in `configuration.yaml`)
  - New script: `script.import_recipe_from_url` — calls `mealie.import_recipe`, clears input, fires refresh event
  - New popup: `/Volumes/config/dashboards/popups/recipe_import_popup.yaml` (Cancel/Import buttons, same pattern as `meal_selection_popup.yaml`)

- **Mealie Password Reset**
  - Reset password for user `bennbennett` via admin API (generate-token → reset-password flow)

## [January 18, 2026]

### Added
- **Home Hub Dashboard** (`/home-hub/rooms`)
  - New modern iPad dashboard with collapsible sidebar and sage green accent color scheme
  - Completely separate from existing tablet-dashboard (does not overwrite it)

  **Design System:**
  - Sage Green Primary: `#4A7C59`
  - Sage Green Light: `#E8F0EA` (active nav backgrounds)
  - Background: `#F9FAFB` (off-white)
  - Cards: `#FFFFFF` (pure white)

  **Features:**
  - Collapsible sidebar (260px expanded, 64px collapsed)
  - Weather widget using `weather.pirateweather` (temp, condition, H/L, humidity, wind)
  - Navigation with active state highlighting
  - Modern room cards with temperature display and light status indicators
  - Scene buttons row (Relax, All Off, Bright, Morning, Good Night)

  **Views:**
  - Rooms (`/home-hub/rooms`) - Room cards with scene buttons (default view)
  - Calendar (`/home-hub/calendar`) - Week planner calendar
  - Tasks (`/home-hub/tasks`) - Shopping list and family todo
  - Meals (`/home-hub/meals`) - Mealie meal planning
  - Devices (`/home-hub/devices`) - Device controls
  - Family (`/home-hub/family`) - Family/people view
  - Toby (`/home-hub/toby`) - Toby's checklists and room controls

  **Files Created:**
  - `/Volumes/config/dashboards/home-hub.yaml` - Main dashboard definition
  - `/Volumes/config/dashboards/home-hub/button_card_templates.yaml` - Button card templates (prefixed `home_hub_`)
  - `/Volumes/config/dashboards/home-hub/decluttering_templates.yaml` - Sidebar assembly templates
  - `/Volumes/config/dashboards/home-hub/views/*.yaml` - Individual view files (7 views)

  **Helper Entity:**
  - `input_boolean.sidebar_collapsed` - Controls sidebar expand/collapse state (added to configuration.yaml)

  **Status:** Work in progress - sidebar layout being refined (expanded sidebar overlap and collapsed weather icon alignment)

## [January 29, 2026]

### Added
- **Home Hub Front House Popup (New UI)**
  - Created new popup layout with custom header + lighting controls
  - Includes three light sliders: `light.front_house`, `light.living_room_color`, `light.extended_color_light_1`
  - Added scene buttons: Relax (`scene.front_house_relax`), Energize (`scene.front_house_energize`), Night (`scene.front_house_nightlight`)
  - File: `/Volumes/config/dashboards/popups/front_house_popup.yaml`

### Changed
- **Home Hub Rooms (Front House Card Behavior)**
  - Tap now opens the new popup instead of toggling lights
  - Light toggle moved to the status icon only
  - File: `/Volumes/config/dashboards/home-hub/decluttering_templates.yaml`

## [December 16, 2025]

### Fixed
- **Toby Dashboard Checklists - Missing Entities**
  - School, Swimming, and Hockey checklists showed orange question marks (entities unavailable)
  - Root cause: Dashboard (toby.yaml) used different entity naming than configuration.yaml
  - Added 28 missing `input_boolean` entities to configuration.yaml:
    - **School checklist** (7 items): `school_snack`, `school_lunch`, `school_water`, `school_jacket`, `school_binder`, `school_chromebook`, `school_homework`
    - **Swimming checklist** (12 items): `swimming_bag`, `swimming_shirt`, `swimming_trunks`, `swimming_goggles`, `swimming_towel`, `swimming_sunscreen`, `swimming_wet_bag`, `swimming_underwear`, `swimming_shirt_change`, `swimming_shorts`, `swimming_water`, `swimming_snack`
    - **Hockey checklist** (9 items): `hockey_1` through `hockey_8`, `hockey_jersey`
  - Required HA restart to initialize new entities

## [December 15, 2025]

### Changed
- **Adaptive Lighting Color Temperature Range**
  - Increased `min_color_temp` from 2000K to **2700K** (all rooms)
  - Increased `sleep_color_temp` from 1800K/1900K to **2200K** (Toby's Room & Bedrooms)
  - Reason: 2000K appeared too dim (perceptual dimming from warm orange light)

- **Transition Times Extended to 2 Minutes**
  - `adaptive_lighting.yaml`: All rooms now use 120s transitions (was 30-60s)
  - `automations.yaml`: Hourly automation transitions now 120s (was 30s)
  - Reason: Make color temperature changes less noticeable

- **Hourly Automation Renamed**
  - "Hourly Adaptive Temperature - All Rooms (30s)" → "Hourly Adaptive Temperature - All Rooms (2min)"

### Fixed
- **CLAUDE.md API Access Instructions**
  - Changed `source .env` to `. .env` (more reliable in Claude Code context)
  - Added guidance to save large API responses to temp file before parsing
  - Piping large responses directly to Python fails due to buffering issues

- **Template Light Migration (HA 2026.6 Deprecation)**
  - Migrated `outdoor_lights_dimmable` from legacy `platform: template` syntax to modern `template:` section
  - Moved light definition into `configuration.yaml` under existing `template:` block
  - Commented out `light: !include lights.yaml` (no longer needed)
  - Addresses HA warning about legacy syntax removal in version 2026.6

## [December 2024]

### Added
- **Unified Hourly Adaptive Temperature Automation** (`hourly_adaptive_temp_all_rooms`)
  - Replaces separate front house and bedroom automations
  - Covers 11 lights across Front House, Master Bedroom, and Toby's Room
  - Runs every hour at `:00` with 30-second transition
  - **Only affects lights currently ON** - never turns on lights that are off
  - Preserves each light's current brightness
  - Uses `switch.adaptive_lighting_living_room` for color temp values
  - Lights covered:
    - Front House: living_room_color, kitchen_color, kitchen_color_1, dining_room_color_1, dining_room_color_2, extended_color_light_1
    - Master Bedroom: hue_color_lamp_1, hue_color_lamp_1_2, hue_color_lamp_1_3
    - Toby's Room: toby_s_room_color, toby_s_room_color_2

- **Shed Door Sensor to Dashboard**
  - Added `binary_sensor.door_sensor_shed` to Outside card
  - Shows as second door icon next to existing outside door
  - Green when closed, red when open

- **Documentation Restructure**
  - Created `CLAUDE.md` for Claude Code session context
  - Created `docs/` directory with INDEX.md
  - Moved tools to `tools/` directory
  - Fixed hardcoded credentials in `monitor_lights.py`

### Changed
- Updated `button_card_templates.yaml` to support `door_entity_2` variable

### Removed
- `fp2_front_house_hourly_adaptive_temp` - replaced by unified automation
- `fp2_bedroom_hourly_adaptive_temp` - replaced by unified automation

### Fixed
- **Automation turning on lights that were off** - Original automation used Hue groups/zones which turn on ALL lights when called. New automation checks each individual light and only applies changes to lights already ON.

## [November 15, 2024]

### Added
- **Calendar Card Pro** integration for iPad dashboard
- Calendar view with custom colors for 6 calendars

## [November 13, 2024]

### Added
- **Initial Setup**
  - Created `.env` with Home Assistant credentials
  - Created `hass-setup.sh` helper script
  - Created `monitor_lights.py` for debugging light changes
  - Created `README.md` and `HOME_ASSISTANT_DOCS.md`

- **Template Light for KP405**
  - Created `light.outdoor_lights_dimmable` template entity
  - Exposes dimming capability that TP-Link integration missed
  - File: `/Volumes/config/lights.yaml`

- **Samba File Access**
  - Set up Samba mount at `/Volumes/config/`
  - Created symlink `ha_config/` for easy access

### Changed
- **Adaptive Lighting Configuration**
  - Disabled brightness adaptation for all rooms
  - Kept color temperature adaptation enabled
  - Rooms affected: Living Room, Kitchen, Toby Room, Bedrooms

### Removed
- Speaker entities from dashboard (speakers physically removed)
  - `media_player.speakers`
  - `media_player.living_room_wifi`
  - `media_player.kitchen_wifi`
  - Plus 4 UUID-based speaker entities

### Fixed
- **Mystery Light Dimming Issue**
  - Root cause: Adaptive Lighting was controlling brightness
  - Solution: Configured for color-only mode

- **Outdoor Lights Dimming**
  - KP405 dimmer wasn't exposing brightness control
  - Solution: Template light wrapper to properly expose dimming

---

## Session Archive

Detailed session logs from November 2024 are preserved in:
`history/sessions/2024-11-13.md`
