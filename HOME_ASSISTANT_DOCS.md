# Home Assistant Documentation & Reference
*Last Updated: April 19, 2026*

## Quick Start for Claude Code

### Login Process (Recommended)
```bash
cd /Users/bbennett/Documents/25_PERSONAL-Environment/home-assistant
source .env
export HASS_URL HASS_TOKEN
./hass-setup.sh test
```

### Access Configuration Files via Samba
```bash
# Open Samba connection (may prompt for credentials)
open "smb://192.168.68.114/config"

# Files will be mounted at:
/Volumes/config/
```

## Most Recent Work (Jan 29, 2Y)
## Most Recent Work (Feb 23, 2026)
✅ Refined Home Hub Meals view to closely match mockup screenshots
  - Added/updated weekly dinners container, day pills, and recipe card visual hierarchy
  - Added functional recipe search and category filters
✅ Fixed Recipe Browser click behavior
  - Removed root card interaction conflict so search input, chips, and recipe cards are clickable
✅ Added clear/cancel meal assignment flow
  - Added `Clear` action in meal selection popup
  - Added `script.clear_meal_for_day`
  - Implemented sentinel-title mapping (`__HA_CLEARED__`) in mealplan fetch transform so cleared days render as `+ Dinner`
✅ Updated docs/changelog references for Mealie and Home Hub meals fixes

## Most Recent Work (Jan 29, 2Y)
✅ Updated Tailscale connection (100.116.131.121) for remote access
✅ Overhauled Devices View styling to match modern mockup
  - Replaced large cards with sleek Filter Pills (Sage Green accent)
  - Redesigned Device Cards with square icon boxes and sub-labels
  - Added Wi-Fi indicators and battery/location status to main cards
✅ Created New iPhone Popup
  - Visual battery level bar
  - Network and Location status rows
  - Quick Actions grid (Ring Device, Play Sound, etc.)
  - Relative 'Last seen' footer
✅ Updated project documentation

## Most Recent Work (Jan 12, 2026)
✅ Updated Home Assistant IP address (192.168.68.108 → 192.168.68.114)
✅ Created 3D Printer LED strip automations (using `light.the_abyss`)
  - LED turns ON when print starts (printing, preheating, homing, leveling)
  - LED turns OFF when print ends (idle, complete)
✅ Created Weekday Morning Kitchen/Dining automation
  - Turns on `light.dining_kitchen_zone` at 6:15 AM Mon-Fri
  - 15% brightness with adaptive color temperature
✅ Updated project documentation

## Most Recent Work (Jan 18, 2026)
✅ Fixed Home Hub sidebar overlap and collapsed rail alignment
✅ Migrated Rooms, Calendar, Tasks, Devices, Family views to new pattern
✅ Added 16px gap and single top‑level card to satisfy panel mode
✅ Extracted per‑view main content into decluttering templates
✅ Fixed calendar popup include path (use absolute `/config/dashboards/popups/...`)
⭕ Pending: Migrate Meals and Toby views to new pattern

### Home Hub Sidebar Pattern (Summary)
- Two static `layout-card` grids per view, swapped by `input_boolean.sidebar_collapsed`:
  - Expanded: `grid-template-columns: 260px 1fr`
  - Collapsed: `grid-template-columns: 64px 1fr`
- 16px `grid-gap` prevents any visual overlap/shadow bleed
- Single top-level `vertical-stack` card (panel view requirement)
- Main content is a decluttering template (`home_hub_<view>_main`) returning one `vertical-stack`, pinned to column 2

### Modified Files (Key)
- `/Volumes/config/dashboards/home-hub/views/rooms.yaml`
- `/Volumes/config/dashboards/home-hub/views/calendar.yaml`
- `/Volumes/config/dashboards/home-hub/views/tasks.yaml`
- `/Volumes/config/dashboards/home-hub/views/devices.yaml`
- `/Volumes/config/dashboards/home-hub/views/family.yaml`
- `/Volumes/config/dashboards/home-hub/decluttering_templates.yaml` (added `home_hub_*_main` templates)

### Known Notes
- Calendar: if neither `calendar_week_view` nor `calendar_month_view` is ON, the Home Hub calendar shows Month by default (fallback) to avoid a blank view. iPad dashboard calendar remains unchanged and can be used for reference.

## Previous Work (Nov 15, 2024 - 10:05 AM)
✅ Replaced week-planner-card with Calendar Card Pro
✅ Installed Calendar Card Pro via HACS
✅ Configured all 6 calendars with custom colors
✅ Backed up old calendar configuration
✅ Updated documentation with file locations

## Previous Work (Nov 13, 2024 - 11:45 PM)
✅ Fixed outdoor lights dimming - created template wrapper for KP405
✅ Removed all speaker entities from dashboard (speakers physically removed)
✅ Disabled Adaptive Lighting brightness (kept color temperature changes only)

## System Overview

### Connection Details
- **URL:** http://192.168.68.114:8123
- **Token Name:** Claude MCP
- **Token:** Stored in `.env` file (expires 2073)
- **Version:** Home Assistant 2026.4.3
- **Location:** Home (America/Los Angeles)
- **Time Zone:** America/Los_Angeles

### Key Statistics
- **Total Entities:** 650+
- **Automations:** 25 total (21 enabled)
- **Integrations:** 198 components loaded
- **Major Integrations:** Nest, TP-Link, Tuya, Philips Hue, Roomba, ZHA (Zigbee), HACS

## Current Configuration Status

### ✅ What's Working
1. **API Access** - Full access configured and saved
2. **Adaptive Lighting** - Color temperature changes ONLY (no brightness)
3. **Automation Status** - Only 2 automations running (checklist resets at midnight)

### 🔧 What We Changed Today (Nov 13, 2024)

#### 1. Mystery Light Dimming - SOLVED
- **Problem:** Lights were dimming at 8pm and 10pm mysteriously
- **Cause:** Adaptive Lighting was controlling brightness automatically
- **Solution:** Disabled brightness adaptation, kept color temperature changes only
- **Result:** Lights now change color (cool→warm) but stay at your set brightness

#### 2. Home Assistant Access Setup
- Created configuration folder: `~/25_PERSONAL-Environment/home-assistant/`
- Saved credentials securely in `.env`
- Created helper script `hass-setup.sh`
- Created monitoring tools

#### 3. Adaptive Lighting Configuration
**Current Settings per room:**
- Living Room: ✅ Color-Only Mode
- Kitchen: ✅ Color-Only Mode
- Toby Room: ✅ Color-Only Mode
- Bedrooms: ✅ Color-Only Mode

## Dashboard Information

### iPad Dashboard
- **URL:** http://192.168.68.114:8123/lovelace/ipad
- **Device:** Benjamin's iPad (tracked in system)
- **Main Config:** `/Volumes/config/dashboards/tablet.yaml`

### Dashboard File Structure
```
/Volumes/config/dashboards/
├── tablet.yaml                      # Main tablet dashboard config
├── resources.yaml                   # Custom card resources (JS files)
├── button_card_templates.yaml       # Reusable button templates
├── decluttering_templates.yaml      # Reusable card templates
└── views/                           # Individual view files
    ├── calendar.yaml                # Calendar view (Calendar Card Pro)
    ├── devices.yaml                 # Device tracking view
    ├── home.yaml                    # Home view
    ├── people.yaml                  # People tracking view
    ├── rooms.yaml                   # Room controls view
    ├── tasks.yaml                   # Task management view
    ├── toby.yaml                    # Toby-specific view
    └── toby-bored.yaml              # Toby boredom activities
```

### Dashboard Controls
- **Menu Items:** Calendar, Tasks, Rooms, Electronics, People
- **Device Filters:** All, Phones, Tablets, Computers

### Dashboard Entities
```yaml
Menu Controls:
- input_boolean.menu_calendar
- input_boolean.menu_tasks
- input_boolean.menu_rooms
- input_boolean.menu_electronics
- input_boolean.menu_people

Device Filters:
- input_boolean.device_filter_phones
- input_boolean.device_filter_tablets
- input_boolean.device_filter_computer
```

## Disabled Automations (Found but Inactive)

These automations exist but are turned OFF:
1. **Early Evening Wind Down** - Last run: April 2025
2. **Bedtime Cue** - Last run: June 2025
3. **Evening Brightness Adjustment** - Last run: June 2025
4. **Sunset Gradual Lighting** - Last run: June 2025
5. Various Hallway light sync automations
6. Swimming checklist automations

## Quick Command Reference

### Test Connection
```bash
~/25_PERSONAL-Environment/home-assistant/hass-setup.sh test
```

### Get Entity Summary
```bash
~/25_PERSONAL-Environment/home-assistant/hass-setup.sh summary
```

### Turn On/Off a Light
```bash
# Turn on
curl -X POST -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room"}' \
  $HASS_URL/api/services/light/turn_on

# Turn off
curl -X POST -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room"}' \
  $HASS_URL/api/services/light/turn_off
```

### Monitor Light Changes
```bash
python3 ~/25_PERSONAL-Environment/home-assistant/monitor_lights.py
```

### Adaptive Lighting Control
```bash
# Turn off all Adaptive Lighting
for room in "living_room" "kitchen" "toby_room" "bedrooms"; do
  curl -X POST -H "Authorization: Bearer $HASS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"entity_id\": \"switch.adaptive_lighting_${room}\"}" \
    $HASS_URL/api/services/switch/turn_off
done

# Turn off just brightness (keep color)
curl -X POST -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "switch.adaptive_lighting_adapt_brightness_living_room"}' \
  $HASS_URL/api/services/switch/turn_off
```

## Common Tasks

### Check What Changed Recently
```bash
curl -s -H "Authorization: Bearer $HASS_TOKEN" \
  $HASS_URL/api/logbook?period=1 | python3 -m json.tool | less
```

### Reset All Dashboard Toggles
```bash
# Turn off all menu items
for menu in calendar tasks rooms electronics people; do
  curl -X POST -H "Authorization: Bearer $HASS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"entity_id\": \"input_boolean.menu_${menu}\"}" \
    $HASS_URL/api/services/input_boolean/turn_off
done
```

### Check Device States
```bash
# Get all lights
curl -s -H "Authorization: Bearer $HASS_TOKEN" $HASS_URL/api/states | \
  python3 -c "import sys,json; [print(s['entity_id']) for s in json.load(sys.stdin) if s['entity_id'].startswith('light.')]"
```

## Calendar Configuration

### Calendar Card Pro (Current Setup - Nov 15, 2024)
- **Card Type:** custom:calendar-card-pro
- **Config File:** `/Volumes/config/dashboards/views/calendar.yaml`
- **Resource:** `/Volumes/config/www/community/calendar-card-pro/calendar-card-pro.js`
- **Old Config Backup:** `/Volumes/config/dashboards/views/calendar.yaml.backup-20241115-100459`

### Available Calendars (6 total)
```yaml
calendar.home_calendar           # Yellow (#e6c229) - Home events
calendar.meals                   # Teal (#5F9EA0) - Meal planning
calendar.birthdays_anniversaries # Purple (#9333EA) - Birthdays & anniversaries
calendar.ben_personal            # Blue (#3B82F6) - Personal events
calendar.work_calendar           # Red (#DC2626) - Work events
calendar.holidays_in_united_states # Red (#FF0000) - US holidays
```

### Calendar Card Features
- Shows next 30 days of events
- Event times, locations, and descriptions
- Progress bars for ongoing events
- Countdown timers for upcoming events
- Weather integration (weather.home)
- List-based layout (not grid)

### To Modify Calendar View
1. Mount Samba: `open "smb://192.168.68.114/config"`
2. Edit: `/Volumes/config/dashboards/views/calendar.yaml`
3. Refresh dashboard in browser

## Accessing Configuration Files via Samba

### Quick Connect
```bash
# Open Finder connection to Home Assistant config
open "smb://192.168.68.114/config"

# Enter your Home Assistant username and password when prompted
```

### Available Samba Shares
- `config` - Main configuration directory (YAML files)
- `backup` - Backup directory
- `addons` - Add-ons directory
- `media` - Media files
- `share` - Shared directory

### Mounted Location
After connecting via Finder: `/Volumes/config/`

### Key Configuration Files
- `/Volumes/config/configuration.yaml` - Main config
- `/Volumes/config/automations.yaml` - Automations
- `/Volumes/config/dashboards/tablet.yaml` - iPad dashboard (main entry)
- `/Volumes/config/dashboards/resources.yaml` - Custom card JS resources
- `/Volumes/config/dashboards/views/calendar.yaml` - Calendar view config
- `/Volumes/config/dashboards/views/rooms.yaml` - Room cards
- `/Volumes/config/dashboards/button_card_templates.yaml` - Card templates

## File Structure
```
~/25_PERSONAL-Environment/home-assistant/
├── .env                        # Credentials (don't share!)
├── hass-setup.sh              # Helper script
├── monitor_lights.py          # Light monitoring tool
├── README.md                  # Setup instructions
├── HOME_ASSISTANT_DOCS.md    # This file
├── session_history.log        # Session history
└── ha_config/                 # Symlink to /Volumes/config when mounted
```

## Troubleshooting

### Issue: Can't connect to Home Assistant
1. Check if HA is running: `ping 192.168.68.114`
2. Verify token hasn't expired in HA UI
3. Re-source the setup script

### Issue: Lights changing unexpectedly
1. Check Adaptive Lighting status (should be color-only)
2. Look for enabled automations
3. Check Hue app for native schedules
4. Run monitor_lights.py to track changes

### Issue: Dashboard not loading
1. Clear browser cache
2. Check URL: http://192.168.68.114:8123/lovelace/ipad
3. Verify entities exist using the states API

## Recent Fixes

### KP405 Outdoor Dimmer Fix (Nov 13, 2024 - 11:30 PM)
**Problem:** Outdoor lights (KP405 Kasa Smart Outdoor Dimmer) wouldn't dim via Home Assistant but worked in Tapo app
**Cause:** TP-Link Smart Home integration doesn't properly detect KP405's dimming capability
**Solution:** Created template light wrapper to expose dimming functionality

**How to use:**
- Entity name: `light.outdoor_lights_dimmable` (replaces `light.outdoor_lights`)
- Full dimming control now available in UI and dashboard
- Configuration in: `/Volumes/config/lights.yaml`

## Notes for Next Session

### Pending Tasks
- [ ] Clean up iPad dashboard (user wants to specify requirements)
- [ ] Possibly remove unused dashboard menu items
- [ ] Consider re-enabling some evening automations with modifications
- [ ] Monitor 3D printer LED automations to ensure they work correctly
- [ ] Check if `light.printer_light` entity becomes available (was unavailable after Hue room move)

### Recent Changes (Jan 2026)
- Home Assistant IP changed: 192.168.68.108 → 192.168.68.114
- New automation: 3D Printer LED strip on/off (uses `light.the_abyss`)
- New automation: Weekday morning kitchen/dining lights at 6:15 AM (15% brightness)
- Printer LED strip moved to "The Abyss" room in Hue (isolated from other rooms)

### Key Entities for 3D Printer LED
- `light.the_abyss` - Hue room containing the printer LED strip (works)
- `light.printer_light` - Individual light entity (was unavailable, may need Hue integration refresh)

## Session History
See `session_history.log` for detailed history of all changes made.

## Popup Patterns & Best Practices (Browser Mod)

This captures what worked best when building device‑agnostic popups for the iPad dashboard, including styling, centering, and create/close behavior.

- Popup files:
  - Content: `/Volumes/config/dashboards/popups/calendar_event_popup.yaml`
  - Add Event button: `/Volumes/config/dashboards/views/calendar.yaml`
  - Open/submit scripts: `/Volumes/config/scripts.yaml`

- Open/close behavior:
  - Use `browser_mod.popup` with `data.content` (not `data.card`).
  - Device‑agnostic close: front‑end sequence via `fire-dom-event` → `browser_mod.sequence` → `[script.create_calendar_popup_event, browser_mod.close_popup]`.
  - Avoid backend `close_popup` without a `browser_id` (it won’t know which device to close).

- Width and styling:
  - Set dialog width to 50% with Browser Mod style: `.mdc-dialog .mdc-dialog__surface { width: 50vw; max-width: 50vw; }`.
  - Also apply `card_mod` to the root popup stack: `:host { width: 50vw; max-width: 50vw; margin: 0 auto; }`.
  - Don’t wrap a `markdown` card in `mod-card` — apply `card_mod` directly on the `markdown` card.

- Centering rows (reliable):
  - Wrap rows in `custom:layout-card` with `layout_type: custom:grid-layout`.
  - Use side gutters to center content: e.g., columns `1fr max-content max-content 1fr` (buttons pinned to columns 2/3) or `1fr … 1fr` for three buttons.
  - Pin each button using `view_layout.grid-column` (2, 3, 4, etc.).
  - Add `card_mod` to give the layout card `width: 100%` so the center gutters work.

- Entities/helpers used:
  - `input_select.calendar_selector`
  - `input_text.event_title`, `input_text.event_location`, `input_text.event_description`
  - `input_datetime.event_start`, `input_datetime.event_end`
  - `input_boolean.event_all_day`, `input_boolean.event_set_end_time`
  - `input_boolean.event_show_location`, `input_boolean.event_show_description`

- All‑day vs timed events (script logic):
  - Script `create_calendar_popup_event` uses `choose`:
    - All‑day ON → `calendar.create_event` with `start_date` and `end_date = start + 1 day` (required to avoid minimum duration error).
    - All‑day OFF → `start_date_time` and `end_date_time`; default end = start + 1 hour if `event_set_end_time` is OFF.
  - UI rule: show End Time only when `event_set_end_time` is ON and All‑day is OFF.

- Common pitfalls and fixes:
  - Wrong include path from views: use `!include ../popups/calendar_event_popup.yaml`.
  - Popup must use `content:`; using `card:` renders only the title/X.
  - YAML indentation: all items under `cards:` need proper indent; mis‑indent triggers “Configuration error”.
  - After adding helpers, reload them: call `input_boolean.reload`; scripts: `script.reload`.
  - If `.local` WebSocket is flaky, use `http://192.168.68.114:8123`.

- Quick reloads (after edits):
  - `curl -X POST "$HASS_URL/api/services/input_boolean/reload" -H "Authorization: Bearer $HASS_TOKEN"`
  - `curl -X POST "$HASS_URL/api/services/script/reload" -H "Authorization: Bearer $HASS_TOKEN"`
  - Refresh the dashboard in the browser.

---
*This documentation is maintained in `~/25_PERSONAL-Environment/home-assistant/` for easy access in future Claude Code sessions.*
