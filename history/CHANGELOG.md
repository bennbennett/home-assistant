# Home Assistant Changelog

All notable changes to the Home Assistant configuration.

## [April 11, 2026 — Countertop QA + P0 Fixes (Post-Phase 4)]

QA session scored the live Countertop dashboard 33/40 against the mockup. Three P0 regressions fixed, plus one pre-existing bug discovered and fixed. Full QA report at `qa-2026-04-11/REPORT.md`.

### Fixed
- **Meals view scene bar no longer hidden offscreen.** The recipe browser content was pushing the persistent scene bar 5px past the viewport bottom (`top: 773, viewport: 768`). Changed `grid-template-rows` from `1fr auto` to `minmax(0, 1fr) auto` so the first row actually shrinks to fit. Scene bar now measures at `bottom: 751`, comfortably visible
- **Input patcher now reaches ha-textfield inside shadow roots.** The `patchInputFields()` function in `home-hub-fonts.js` was exiting early on every input field because `row.querySelector('ha-textfield')` only searches light DOM, but `ha-textfield` lives inside `hui-input-text-entity-row`'s shadow root. Added a `findInShadow()` recursive walker. Both the Toby Add Activity field and the Shopping List popup input are now styled with the custom border, terracotta focus ring, and hidden HA chrome
- **Dinner popup commits meals.** Two-part fix. (1) Replaced the broken input_select dropdown + standalone "Assign To Tonight" button with a 2x3 grid of recipe cards. Each card passes its recipe name directly to the script via `service_data`, no state round-trip. (2) Discovered a pre-existing bug: `mealie.get_recipes` does NOT populate the `id` field in its response, so `assign_meal_to_day`'s recipe_id lookup always returned empty and the script silently exited. Created `scripts/assign_meal.sh` that resolves slug to UUID via Mealie's REST API, then POSTs the mealplan entry directly. The `assign_meal_to_day` script now uses `shell_command.mealie_assign_meal` with the slug instead of the broken `mealie.set_mealplan`

### Added
- **`scripts/assign_meal.sh`** — Shell script that looks up a recipe UUID from its slug via Mealie API, then creates a mealplan entry. Reads auth token from `secrets.yaml`. Bypasses the broken HA Mealie integration for this one operation
- **`shell_command.mealie_assign_meal`** — HA shell command entry in `configuration.yaml` that calls the assign script with `slug` and `date` template variables

### Technical
- Cache-bust bumped from `?v=3` to `?v=4` on `home-hub-fonts.js` in `configuration.yaml`
- `automations.yaml` recipe fetch updated to try `r.recipe_id` and `r['id']` fallback for the UUID field (may help if a future HA update exposes the field)
- QA was performed via gstack browse at 1024x768 with long-lived token injection into `localStorage.hassTokens`. Auth must be re-injected before each `goto` navigation
- All fixes were applied directly to `/Volumes/config` over Samba, then verified after two HA restarts

## [April 11, 2026 — The Countertop Phase 4: Live Remediation]

Seven of the eight broken interactions from Phase 3 now work. Shopping and Toby Add Activity fields actually accept typing on iPad (including the spacebar). The kitchen timer popup shows a live countdown with a draining terracotta ring. The Home weather block is no longer dead — tap it for an hourly forecast. The dinner popup still has a broken assignment action, which is the one remaining gap from this cycle. Full session log at [`docs/12-countertop-live-remediation-2026-04-11.md`](../docs/12-countertop-live-remediation-2026-04-11.md).

### Changed
- **Shopping list popup actually works on iPad.** The input field accepts typing and the spacebar, the Add button fires the service call, and the popup reads like part of the dashboard instead of an HA admin dialog. Rebuilt around an `entities` card wrapping `input_text.add_to_list_item` + a native button calling `script.ct_add_to_shopping_list`
- **Toby Add Activity inline field works.** Same rebuild pattern as the shopping popup but inline on the Toby page. Text entry, spacebar, and Add all work. The visual shell still merges into the Bored card as one continuous block
- **Kitchen timer popup shows a live countdown and ring.** Previously the popup could display a snapshot of timer state, but the ring and countdown didn't animate once the popup opened. Switched the popup renderer to `custom:simple-timer-card` (which maintains its own update interval) and it now updates in real time. Pause/Cancel only appear when the timer is active or paused; idle state shows presets only
- **Home weather area opens an hourly forecast popup.** Tapping the Home header opens a Browser Mod popup with the warm-tinted hourly weather strip. Narrowing the tap target to the weather block only (instead of the whole header) is a known follow-up
- **Find Phone uses a transient top-center toast.** Replaced the modal-style feedback with a Browser Mod toast restyled via `home-hub-fonts.js`. No dimming overlay, no modal shell, auto-dismisses
- **Toby Manage popup controls seasonal visibility.** The `season_school` / `season_swimming` / `season_hockey` booleans in the popup now actually show/hide their respective checklist cards on the Toby page. Calm empty state renders if all three are off
- **Hockey checklist restored.** Hockey had been removed in an earlier pass. Reintroduced `input_boolean.season_hockey` in the Manage popup, restored the Hockey checklist card on the Toby page, and added Hockey icon mappings to the checklist template
- **Home tile timer countdown animates.** The tile itself computes remaining time client-side so the mm:ss text ticks on the Home screen, not just inside the popup

### Added
- **`custom:simple-timer-card` resource** — New popup timer renderer that replaces `circular-timer-card`. Added to `dashboards/resources.yaml`. `circular-timer-card` stays installed but is no longer wired up
- **`countertop_assign_meal_to_tonight` script** — Wrapper in `scripts.yaml` that reads today from `now().strftime('%A')`, sets it on `input_select.meal_day_selector`, sets the recipe on `input_select.recipe_selector`, and fires the existing `assign_meal_to_day` flow. Falls back to the current selector value if no recipe is explicitly passed (needed for the native selector-driven popup approach)
- **`countertop_kitchen_timer_finished_alert` automation** — Listens for `timer.finished` on `timer.kitchen_timer` and sends an audible critical notification to the mounted iPad. The kitchen beeps when the timer runs out
- **Hourly weather popup partial** — `dashboards/popups/countertop_hourly_weather_popup.yaml`, wired to the Home header tap action
- **Best-effort screen wake lock** — `home-hub-fonts.js` now requests wake lock while `timer.kitchen_timer` is active, route-gated to Countertop. Releases when the timer stops, the page is hidden, or you navigate away. Falls back silently if Safari declines

### Fixed
- **Browser Mod popup inputs broken on iPad Safari.** Custom HTML `<input>` elements inside button-card JS templates couldn't reliably hold focus, accept spacebar, or dispatch tap actions through the popup DOM. Root fix: stop rendering controls as raw HTML inside popups. Every broken input got rebuilt as an `entities` card wrapping `input_text` + a service-call button-card, with `home-hub-fonts.js` patching the `ha-textfield` shadow DOM to strip HA form chrome. This pattern is the unifying insight from the pass — it can be reused anywhere an input needs to live inside a popup
- **`circular-timer-card` didn't animate in popups.** The card could render a correct static position but didn't maintain an update loop, so the ring froze as soon as the popup opened. `simple-timer-card` has the internal interval and animates correctly

### Known gaps
- **Dinner popup assignment still doesn't commit.** The popup shell opens and reads correctly, but tapping "Assign to Tonight" doesn't write the assignment. Next pass needs to isolate the selected recipe value at click time, validate the wrapper script call path inside the popup context, and decide whether the popup should close or refresh after assignment. Tracked as the single open item from this remediation cycle
- **Find Phone toast** not re-verified in the final live cycle — the target iPhone was unavailable to disturb
- **Weather popup tap target** is the whole Home header, not just the weather block. Functional, but a known refinement

### Technical
- Work was performed directly against `/Volumes/config` over Samba. The repo copy was not treated as authoritative for this pass
- **Native Lovelace inside Browser Mod was the pivot.** Every broken control got rebuilt the same way: `entities` card → `input_text` → service-call button-card → shadow DOM patch for visual polish. Bubble Card was available but deliberately not introduced — Browser Mod + native controls + shadow DOM patching was enough
- **`home-hub-fonts.js` patches after this pass**: Fraunces loading, shared animation keyframes, hourly-weather warm style, Countertop sparse-view vertical centering, top-center toast restyle, wake lock gated to `timer.kitchen_timer`, and the native `ha-textfield` shadow DOM input patch
- Timer popup went through four implementations (existing custom → more custom HTML → `circular-timer-card` → `simple-timer-card`) before landing on one that animated live

## [April 10, 2026 — The Countertop Phase 3: Final Polish]

Three rounds of second-opinion review closed the remaining visual/interaction gaps. Inputs no longer look like HA admin forms, popups feel like part of the dashboard, and Find Phone no longer dims the screen.

### Changed
- **Checklist popups redesigned** — School and Swimming popups now use custom `ct_checklist_item` rows instead of HA's default entities-card toggle switches. Each row has a left-side checkbox (green/blue fill when checked), a 36x36 tinted icon tile, and a 15px label with strikethrough on completion. Reads like a packing list, not a settings page
- **All popup chrome hidden** — Shopping list, timer, phone toast, and both checklists now use `popup_styles` to hide the HA dialog header and set 24px border-radius. Titles rendered as Fraunces serif inside the popup content
- **Timer idle state cleaned up** — Pause/Cancel buttons only appear when the timer is active or paused. Idle state shows presets only
- **Meals uses fixed 7-day grid** — Mon through Sun slots always visible with day labels. Assigned meals show their name, empty slots show a dashed "Add Meal" placeholder. Today's empty slot gets terracotta accent. Grid is always stable regardless of data
- **Find Phone no longer dims the screen** — `--mdc-dialog-scrim-color: transparent` removes the modal overlay. Feedback appears as a floating terracotta pill with `hh-fade-in` animation
- **Action buttons taller** — `min-height` bumped from 140px to 200px, filling more of the iPad's vertical space
- **Room card subtitle removed** — "Lights off" fallback text replaced with empty spacer. The lightbulb icon already conveys state
- **Toby add-activity merged into bored card** — Border-radius hack (16px top on bored card, 16px bottom on add row, no border between) makes them read as one card

### Added
- **JS input field patcher** (`patchInputFields()` in `home-hub-fonts.js`) — Patches `ha-textfield` shadow DOM on countertop routes to hide the MDC underline, floating label, and leading icon. Adds clean 12px-radius bordered input with terracotta focus ring. Handles both inline inputs and popup inputs via recursive DOM walker
- **16 checklist icons** — SVG icon map in `ct_checklist_item` template (apple, lunch, water, jacket, notebook, laptop, pencil, bag, shirt, swim, goggles, towel, sun, droplet, shorts)

### Fixed
- **Swimming progress bar** used hardcoded sage green instead of the card's blue accent color
- **Calendar legend/weather** hidden on week view to reclaim vertical space. `compact: false` gives day cards more room
- **Checklist dividers** softened from cold gray (#F3F4F6) to warm (#F0EFED), padding widened from 4px to 8px for better touch targets

### Technical
- Cache bust: `?v=2` → `?v=3` on `extra_module_url`. HA restart required
- Input patcher uses recursive `findAll` walker (not explicit chain) because popup inputs live inside `browser-mod-popup` elements outside the normal HA shadow DOM tree
- `--mdc-dialog-scrim-color` is a standard MDC CSS variable. If HA switches to native `<dialog>` with `::backdrop`, a JS fallback patcher may be needed

## [April 10, 2026 — The Countertop Phase 2: iPad Visual Fidelity]

Side-by-side comparison of real iPad 6th gen screenshots against the HTML mockup revealed proportion, spacing, and interactivity gaps. Two rounds of fixes closed most of them.

### Fixed
- **Scene bar chips** no longer stretch full-width. Dual-spacer grid pattern (`1fr repeat(5, auto) 1fr`) keeps them as compact centered pills on all 5 views
- **Calendar controls** are now compact left-aligned pills with "+ Add Event" right-aligned (was stretched `horizontal-stack`)
- **Action buttons are taller** (140px min-height, up from 110px) to match mockup proportions on the iPad's 1024x768 viewport
- **Card borders visible on iPad** — darkened from `#F0EDE8` to `#E8E4DE` for arm's-length readability
- **Calendar scene bar always visible** — `max-height: calc(100vh - 210px)` + `compact: true` constrains the planner card so the scene bar doesn't get pushed below the fold
- **Recipe names and cook times now render** — fixed serialization bug where `sensor.mealie_recipe_browser` stored items as a Python repr string instead of a list
- **Vertical centering on Lights and Toby** — JS patcher in `home-hub-fonts.js` sets `height: fit-content` + `alignSelf: center` on the vertical-stack inside grid-layout's shadow root (card_mod can't reach nested shadow roots)
- **Secondary nav links navigate** — "Meals", "Ben", "Petra" are now separate button-cards with tap actions (were inert HTML divs)
- **Agenda and dinner pool are tappable** — navigate to Calendar and Meals respectively (were `tap_action: none`)
- **Find Phone shows feedback** — terracotta toast popup "Ringing Petra's phone..." via `browser_mod.sequence`
- **Recipe text bumped** for arm's-length readability (name 14px, time 12px, image area 80px)
- **Shopping list popup** restyled with inline input+Add layout and "View full list" link

### Added
- **Toby MANAGE button** — same line as CHECKLISTS label, opens season toggle popup (`input_boolean.season_school/swimming/hockey`)
- **Toby Add Activity** — text input + Add button below I'm Bored card. Activities stored in `input_select.toby_activity_selector`, randomizer reads dynamically

### Technical
- iPad companion app WKWebView caches `extra_module_url` JS files aggressively. Force-close and hard reset do NOT clear it. Bump `?v=N` parameter on the URL in `configuration.yaml` + restart HA to bust the cache
- `horizontal-stack` in HA forces equal-width children. Replace with `layout-card` grid using `auto` columns for auto-sizing pills
- `card_mod` `grid-layout$:` nested shadow targeting does not work for layout-card's inner grid. JS DOM patching via `setInterval` is the proven fallback

## [April 9-10, 2026 — The Countertop]

New kitchen fridge iPad dashboard, built from the ground up in 7 staged steps. Hub-and-spoke navigation (5 views, max depth 1), persistent scene bar, designed for an ADHD family of 3 doing quick transactions at arm's length.

### Added
- **The Countertop dashboard** (`/the-countertop/home`) — a new fridge-mounted iPad dashboard separate from the Home Hub. Five views: Home (clock, action grid, agenda, dinner pool), Lights (6 room cards with toggle/hold), Calendar (week-planner-card with week/month toggle), Toby's Corner (School + Swimming checklists, I'm Bored randomizer), and Meals (dinner pool cards, recipe browser)
- **Persistent scene bar** on every view — 5 chips (Relax, All Off, Bright, Morning, Good Night) always visible at bottom, pinned via `layout-card` grid rows
- **Kitchen Timer** — `timer.kitchen_timer` entity with popup showing conic-gradient terracotta countdown disc, 6 preset buttons (5/10/15/20/30/45m), pause/cancel controls. Timer button on Home screen shows live mm:ss countdown when active
- **Add to Shopping List** popup — text input + Add button, writes to Google Keep via `script.ct_add_to_shopping_list`
- **Find Phone** instant action — one tap rings Petra's iPhone (no confirmation dialog, no popup)
- **Checklist popups** — School (7 items) and Swimming (12 items) checklists open as `browser_mod.popup` with toggleable `entities` cards. Summary cards show progress bars

### Technical
- Dashboard key must contain a hyphen (`the-countertop`, not `countertop`) — HA validation requirement
- SVG icons defined inside JS templates as icon-key maps (never as YAML variables — they get HTML-escaped)
- `!include` paths in nested view files resolve relative to the view file's directory (`../scene_bar.yaml`)
- Button-card variables don't support YAML lists — use comma-separated strings, split in JS
- Scene bar uses `grid-template-rows: 1fr auto` (not `position: fixed`)

## [April 7, 2026 — Phase 5: Coherence pass]

After the Editorial Kitchen redesign (Phases 1-4) landed at 24/40, `/critique` flagged two issues that broke the warm direction even though everything else was working: the calendar repeated multi-day events as identical pills across every cell, and the Rooms/Devices/Family icons were still in a leftover Material UI rainbow that didn't sit in the Editorial Kitchen palette. Phase 5 fixes both.

### Changed
- **Calendar week + month views: multi-day events render once instead of seven times.** "ben - spring break" used to fill seven identical "Entire day" pills across the row. Now it appears once on its start day with a clean date range. Same for "Toby spring break". Two actual events now look like two events instead of fourteen visual elements
- **Calendar uses 12-hour AM/PM time** matching the Right Now clock and the hourly forecast. "17:25 - 17:55" → "5:25 PM - 5:55 PM". Time labels are also small uppercase gray now so the event title gets visual priority
- **Calendar drops the redundant "Yesterday/Tomorrow/Thursday" labels** next to day numbers. Today gets a single "TODAY" terracotta eyebrow under the number — one source of "now" signaling instead of two
- **Long calendar event titles truncate to 2 lines** with ellipsis instead of pushing cells to absurd heights
- **Right Now agenda — present-tense labels.** "Until Mon" → "Through Mon" feels more current
- **Right Now agenda — Outlook metadata stripped from event titles.** "Stay at Misty Mountain Chalet- Pets•EV•Trails•Views•2acres" now displays as "Stay at Misty Mountain Chalet". Long titles also ellipsis-truncate cleanly
- **Unified warm icon palette across Rooms, Devices, and Family.** Six colors that all sit in the warm Editorial Kitchen spectrum: sage for Living Room/tablets/batteries, terracotta for Front House/phones/Petra, honey for Kitchen/printers, taupe for Bedroom/work calendar, clay for Toby's Room/Toby avatar/school tile, olive for Outside/ben_personal calendar. Walking from one view to another now feels like one designed system instead of a Material UI grab bag
- **Room cards get tinted tile backgrounds** matching their icon color (14% alpha). Each room is identifiable at a glance AND the icon stays legible without fighting low-contrast strokes. Icon stroke bumped to 28px / weight 2.25 for stronger presence
- **Hourly forecast night blocks no longer harsh black.** Replaced `#111` with warm dusk indigo `#3D3654`. Other forecast colors also slightly warmed (cloudy → warm tan, partlycloudy → softer day blue, sunny → honey yellow)
- **Toby's avatar** changed from cold blue to clay (matches his room and his school tile)

### Fixed
- **week-planner-card v1.14.1 has a config bug** where the `multiDayTimeFormat` key is read as `_multiDayTimeFormat` (with underscore prefix) in the source. Set the YAML key WITH the underscore to actually apply the format. Documented inline so it doesn't get reverted
- **`lovelace-hourly-weather` color variables can't be overridden via card-mod** because they're defined on `.main` inside `weather-bar`'s nested shadow root, which card-mod can't reach. Added a JS patcher to `home-hub-fonts.js` that walks the DOM, finds every `weather-bar` element, and injects a `<style>` tag directly into its shadow root. Runs on script load + every 1.5s to catch newly mounted elements

### Required after pickup
- **Hard refresh on the iPad once** (Safari → close tab → reopen) to pick up the new `home-hub-fonts.js` with the night-block patcher. Without that refresh, the iPad keeps showing black night blocks even though the patch is shipped to disk. Restarting HA also works (it re-busts `extra_module_url` cache)

## [April 4, 2026]

### Changed
- **Design language unified across all Home Hub views** — Every page now shares the same card styling: `16px` border-radius, `1px solid #F3F4F6` border, `0 1px 3px rgba(0,0,0,0.05)` shadow, `20px` padding. Previously, Room cards used `24px` radius with no border, Device cards used `12px` radius with `24px` padding, and Person cards used a stronger `0.1` shadow. Filter/chip pills on the Devices view now match the Calendar and Rooms pill style (`22px` radius, `40px` height, `500` weight, `8px` gap)
- **Popup accent bars added** to Bedroom (green `#5aa287`) and Outside (teal `#549f82`) popups, matching the pattern already used by Living Room, Kitchen, and Toby's Room popups

### Fixed
- **Mealie shopping list auto-sync removed** — The `mealie_google_keep_shopping_list_sync` automation was running every 20 minutes and re-adding stale Mealie grocery items to Google Keep even after they were manually cleared. Removed the `time_pattern` trigger so sync only happens when you press "Send to Keep"

### Added
- **HTML mockup** (`examples/mockup/home-hub-unified.html`) — Interactive mockup of all 6 Home Hub views (Rooms, Calendar, Tasks, Devices, Family, Meals) showing the unified design language. Switchable via bottom tab bar or sidebar navigation

## [April 1, 2026]

### Added
- **Tasks & Lists view** — Two-column layout with Shopping List and Family Todo side by side, each with sage green icon headers and active item counts. Shows both active and completed items matching the mockup
- **Device popups for all devices** — Pixel 10, Small iPad, Big iPad, and Printer now open styled popups instead of default HA more-info. Phones/tablets show battery bar, network status, and Ring Device button. Printer shows 4 CMYK toner level bars (Black, Cyan, Magenta, Yellow)
- **Ring Device scripts** — `script.ring_iphone`, `script.ring_pixel_10`, `script.ring_small_ipad`, `script.ring_big_ipad`. iOS uses critical notification (plays sound even in silent mode). Android uses alarm_stream channel
- **Family member subpages** — Each family member gets a full subpage navigated from the Family gateway:
  - **Toby** (`/home-hub/toby`): School, Swimming, Hockey checklists + "I'm Bored" activity randomizer + Room Controls (lights + temperature)
  - **Ben** (`/home-hub/ben`): Next Event from calendar + 3D Printer status + "Coming Soon" placeholders for Daily Wisdom, Todo List, Commute, Health, Server Stats
  - **Petra** (`/home-hub/petra`): Next Event + Weather + This Week's Meals + "Coming Soon" placeholders for Tide Times, Photography, Todo List
- **Skill routing rules** added to CLAUDE.md for gstack skill auto-invocation

### Changed
- **Family gateway simplified** — Removed Location Overview map and Family Todo list (now on Tasks view). Changed Ben/Petra from popup to navigate action. Header updated to "Family Members" with subtitle
- **Toby view converted** — Migrated from old `max-content` sidebar pattern to standard 198px/64px decluttering template pattern, matching all other Home Hub views
- **iPhone popup cleaned up** — Removed broken `script.find_iphone` (replaced with `script.ring_iphone`), removed Location section, removed Play Sound/Lock Device/Sync Now quick actions (only Ring Device remains)
- **Garmin watch group** — Updated `groups.yaml` to reference `script.ring_iphone` (was `script.find_iphone`)
- **Background color fix** — Tasks, Devices, and Family views updated from `#F9FAFB` to `#fbfaf9` to match all other Home Hub views

## [March 25, 2026]

### Changed
- **Calendar view redesigned** — Home Hub calendar now has a clean header with Week/Month toggle pills and "+ Add Event" button on a separate row below the title (matching the Rooms view layout pattern)
- **Calendar state model simplified** — Replaced two separate booleans (`calendar_week_view` + `calendar_month_view`) with a single `input_select.calendar_view_mode` dropdown. No more invalid "both off" state, no more fallback card
- **Month view shows 4 weeks** — Changed from full calendar month to 28 days starting from the current Monday. Better for weekly planning
- **Today styling cleaned up** — Removed over-designed green circle and left-border accent. Now uses a subtle warm tint with green "Today" text, matching the original mockup
- **Add Event popup split** — Home Hub gets a green-palette popup (`calendar_event_popup_home_hub.yaml`), legacy iPad calendar keeps the original blue version. Each matches its dashboard's color scheme

### Fixed
- **Week view showing 6 days instead of 7** — The week-planner-card's responsive column breakpoints reduced to 5-6 columns when the sidebar narrowed the content area. Fixed by forcing 7 columns at all breakpoints via the card's `columns` config, plus `box-sizing: border-box` on day tiles to prevent padding from pushing the 7th day to the next row
- **Add Event button not opening popup** — Was using `call-service` to a script that calls `browser_mod.popup`, which can't target the current browser. Changed to `fire-dom-event` with inline `browser_mod.popup` (the proven pattern used elsewhere in the dashboard)
- **Toggle scripts simplified** — `toggle_week_view` and `toggle_month_view` now set `input_select.select_option` instead of toggling two booleans in sequence

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
