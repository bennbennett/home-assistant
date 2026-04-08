# Home Hub Critique — Action Plan

> Started: 2026-04-07. Ongoing across multiple sessions.
> Direction: **Editorial Kitchen** — warm-neutral palette + Fraunces serif headings + glance-first landing page. Harmonizes with the Bennett kitchen (white walls, brown wood, beige, light brown carpet).
>
> **Read this file first when resuming.** Update checkboxes as items ship.

## Current score
- Baseline (2026-04-07): **18/40** ("Functional but unrefined")
- After Phase 1-4 (2026-04-07): **24/40** ("Solid")
- After Phase 5 (2026-04-07 cont'd): **~28-30/40** estimate (next /critique to confirm)
- After Phase 6 (2026-04-08): **~30-32/40** estimate (substance + clarity pass)
- Target after all phases: **~33/40**

---

## Phase 6 — Substance & Clarity (2026-04-08)

**Goal**: Card density issue from `/critique` — too much white space — solved with substance, not compression. Plus the leftover failure-state copy and a sidebar simplification pass.

### `/harden` ✅ DONE 2026-04-08
- [x] **Recipe Browser distinguishes Mealie offline from "no recipes"**: when `sensor.mealie_recipe_browser` is `unavailable`/`unknown`, the empty state now reads "Mealie is offline" with a terracotta crossed-circle icon (Fraunces title), instead of misleadingly suggesting the user import family favorites. Fix in `decluttering_templates.yaml` Recipe Browser JS template.
- Toby's Lamp Zigbee badge — still hardware (deferred). Toby room sensor offline copy already shipped Phase 1.

### `/extract` ✅ DONE 2026-04-08
**Substance over compression** — added real information to cards that were 70% empty.
- [x] **Room cards** now show a brightness % line ("65% bright" with sun icon) when the light is on with a brightness attribute. Fills the previously empty middle area. Falls back gracefully when no temp sensor.
- [x] **Person cards** now show **up to 2 events** stacked under UP NEXT (with dashed divider), not just 1. Card height bumped 260→300px and avatar padding tightened (`30px 20px 20px` from `36px 20px 24px`).
- Device cards already have battery in the sub line — left as-is.

### `/onboard` — Ben subpage buildout ✅ DONE 2026-04-08
Ben's page transformed from two anemic mushroom cards into a real personal dashboard:
- [x] **Today's Agenda** (wide left, 1.4fr): rich JS-rendered list of work + personal events for today/tomorrow + active multi-day, with calendar dots (taupe = Work, olive = Personal). Filters `sensor.home_hub_upcoming_events` by `work_calendar` and `ben_personal`. Fraunces "Today's agenda" title + terracotta "Work · Personal" eyebrow. Empty state: "A clear day. Enjoy it." Tap → `/home-hub/calendar`.
- [x] **3D Printer card** (right, 1fr): Fraunces title + status pill (sage when complete, honey when printing, gray when idle). Switches between **printing state** (38px % readout, fill bar, time-left, layer counter, file name) and **idle/complete state** (file name, nozzle/bed temps in °F).
- [x] **Glance stats strip** (bottom): Steps today (with `% of 8k goal`), iPhone battery, iPad battery — Fraunces 26px values with sage/honey/terracotta thresholds (<20% = terracotta, <50% = honey, ≥50% = sage). Charging state in sublabel.
- Petra subpage **deferred** until intentional product convo with user. The earlier speculative ideas (commute, tides, photography, Walmart helper) explicitly NOT shipped.

### `/distill` — Sidebar simplification ✅ DONE 2026-04-08
- [x] **Dropped sidebar weather widget** from both expanded and collapsed sidebars. The Right Now landing already shows the rich weather card; other views can navigate Home if they want it. Removes the duplication called out in `/critique`.
- [x] **Collapsed sidebar nav now has tiny labels** ("Home", "Cal", "Tasks", "Meals", "Rooms", "Devices", "Family") under each icon. Tile bumped from 44×44 to 52×56px. Recognition no longer depends on icon literacy alone — significant accessibility win for kitchen-glance use.

### `/polish`
- [x] Lovelace reloaded
- [x] Action plan updated (this section)
- [ ] User to verify on iPad (hard refresh) and re-run `/critique` for score

---

## Phase 1 — Cleanup (restore trust)

**Goal**: fix the broken stuff so the design has a chance. No styling work until data is clean.

### `/distill` — Cut the dead weight ✅ DONE 2026-04-07
- [x] Re-enable kiosk mode (uncomment `kiosk_mode: kiosk: true` in `home-hub.yaml`, restart HA) — *also had to uncomment the kiosk-mode.js line in `configuration.yaml` extra_module_url; CLAUDE.md was stale*
- [x] Verify HA chrome (sidebar, tab bar) is hidden on iPad after restart — confirmed via Playwright after Ben restarted
- [x] Delete "Coming Soon" placeholder cards from Ben subpage (5 cards)
- [x] Delete "Coming Soon" placeholder cards from Petra subpage (3 cards)
- [x] Decide: family subpages as drill-downs OR top-level tabs — kept as views, kiosk mode hides the duplicate top-tab nav, accessed via Family card click drill-down. No further changes needed.
- [ ] **NEW**: Sidebar nav rendering inconsistent — Ben/Petra/Toby subpages show bordered nav items, Rooms/Calendar/etc. show flat. Investigate in /harden or /polish.

### `/harden` — Fix broken data ✅ DONE 2026-04-07 (mostly)
- [x] Tasks view: set `hide_completed: true` on Family Todo + Shopping List columns
- [x] Tasks view: count headers now use `states('todo.x')` directly (was broken — used `state_attr('items')` which doesn't exist on these entities, always returned 0)
- [ ] Tasks view: optional weekly cleanup automation for items completed > 7 days old (deferred — not blocking)
- [x] Toby's room: fix `unavailable°F` literal text — now shows "Sensor offline" via Jinja conditional
- [ ] Toby's Lamp: yellow `?` Unavailable badge — Zigbee entity is offline. Hardware issue (battery? re-pair?), not a YAML fix.
- [ ] Petra subpage: "Next Event" — there is NO `calendar.petra_personal` entity (only `calendar.ben_personal`, `home_calendar`, and shared ones). Petra continues to use `home_calendar`. **To-do for user**: create a Petra Google Calendar and integrate.
- [x] Ben subpage: switched "Next Event" from `calendar.home_calendar` → `calendar.ben_personal` so his page shows HIS events (was showing the family calendar)
- [x] Devices view: iPad icons fixed — `mdi:tablet-ipad` doesn't render in this MDI version, replaced with `mdi:tablet`. Both Small iPad and Big iPad now show blue tablet icons.
- [x] 3D Printer: shows "Complete" (Title Case) on Ben page — was already working via `| title` filter
- [ ] 3D Printer in Devices view shows "complete" (lowercase) — different template, doesn't apply `| title`. Minor polish.
- [ ] Calendar: all-day events should be a row above timed events. Deferred to `/arrange` since it's a layout change, not data.
- [ ] Sidebar nav rendering inconsistent between Rooms and family subpages (Toby/Ben/Petra). Investigate in `/polish`.

---

## Phase 2 — Glance + Warmth (the highest-impact UX win)

**Goal**: dashboard earns its fridge spot from 6 feet away.

### `/onboard` — Build the "Right Now" landing page ✅ DONE 2026-04-07
- [x] New default landing view at `/home-hub/right-now` — first view in `home-hub.yaml` so it loads by default
- [x] Big clock (128px HH:MM with AM/PM, day of week and full date)
- [x] Big weather card (56px temp + condition + feels-like, sage thermometer icon)
- [x] Today's events list — custom rendering via `sensor.home_hub_upcoming_events` triggered template sensor (populated by `home_hub_fetch_upcoming_events` automation that runs every 5 min and filters all-day spam to today-only)
- [x] Tonight's dinner card (from `sensor.mealie_weekly_meal_plan` — terracotta accent on the icon)
- [x] Time-of-day greeting ("Good evening, Bennetts" via new `sensor.live_greeting`)
- [x] Sidebar reordered: Home (right-now landing), Calendar, Tasks, Meals, Rooms (new), Devices, Family. "Home" now means the glance landing, Rooms is its own item.
- [x] Renamed Rooms page header "Home" → "Rooms"
- New entities created: `sensor.live_time`, `sensor.live_date_long`, `sensor.live_greeting` (30s time pattern), `sensor.home_hub_upcoming_events` (5min events fetch automation)

### `/bolder` — Make glance info actually glanceable ✅ DONE 2026-04-07
- [x] Clock: 128px font, font-weight 300, tabular-nums, letter-spacing -3px (light + spacious)
- [x] Weather temp: 56px font, light weight
- [x] Hero "right now" card on landing page — it's the whole page now
- [x] Terracotta accent (#C87456) introduced — used on tonight's dinner icon and on the "TODAY" eyebrow in the events list. First step toward the warm-neutral palette.
- [x] Added HACS `lovelace-hourly-weather` strip (12 segments, icons only, no header) below the weather/dinner row. Genuinely useful "should I bring a jacket" glance info that answers "what's the rest of today look like".

**HACS dependencies introduced:**
- `lovelace-hourly-weather` ([decompil3d/lovelace-hourly-weather](https://github.com/decompil3d/lovelace-hourly-weather)) — used on the Right Now landing page hourly forecast strip
- (Available but not yet used: `lovelace-digital-clock`, `weather-chart-card`)

### `/arrange` — Fix wasted space ✅ DONE 2026-04-07
- [x] Family page: redesigned with rich person cards (avatar, presence, battery, next event from filtered calendar). New `home_hub_person_card` template uses `sensor.home_hub_upcoming_events` filtered by calendar source. Each card shows: name, At home/Away with colored dot, phone battery (where applicable), UP NEXT block with timed-events-first prioritization. Ben → ben_personal calendar; Petra → home_calendar; Toby → home_calendar (no person entity). Event filter in `home_hub_fetch_upcoming_events` now includes currently-active multi-day all-day events (instead of skipping them) so Ben sees his "Stay at Misty Mountain Chalet — Through tomorrow" entry.
- [x] Right Now agenda renderer updated to group currently-active multi-day events under TODAY with "Until [day]" labels (instead of grouping them under their start date).
- [x] Meals view: duplicate "No meals yet" button removed in earlier session (kept "Make Grocery List →" when filled > 0).
- [ ] Calendar week view: less cramped cells — *deferred* (would require swapping week-planner-card)
- [ ] Recipe Browser header: pull "+ Add Recipe" closer or restructure header — *deferred, minor*

**New patterns introduced:**
- `home_hub_person_card` reads from `sensor.home_hub_upcoming_events` directly (no per-card calendar.get_events) — keeps the dashboard fast.
- Multi-day all-day events labeled as "Through [end-1]" or "Until [day]" rather than just showing start date.
- `hass` is reserved in button-card JS templates (like `html`) — use `haObj` or similar local name.

---

## Phase 3 — Visual Identity (escape the template zone)

**Goal**: stop looking like AI-generated SaaS. Become a thing with a point of view.

### `/typeset` — Install Fraunces serif ✅ DONE 2026-04-07
- [x] Created `/Volumes/config/www/home-hub-fonts.js` that injects Google Fonts Fraunces (variable font, opsz 9..144, weights 300-700) into the document head
- [x] Registered in `frontend.extra_module_url` in `configuration.yaml` as `/local/home-hub-fonts.js`
- [x] Applied Fraunces to ALL `home_hub_header` page titles (34px, opsz 144, letter-spacing -0.5px, weight 400)
- [x] Applied to Right Now hero: greeting (italic Fraunces), AM/PM, full date — clock digits stay system sans for tabular numbers
- [x] Applied to Tonight's Dinner card meal name + "No dinner planned" placeholder
- [x] Applied to "Coming up" agenda eyebrow on Right Now
- [x] Applied to Room card titles ("Front House", "Living Room", etc.) at 18px
- [x] Applied to Person card display names ("Ben", "Petra", "Toby") at 22px
- [x] Applied to "Plan this week" Meals header at 34px (replaces sans 24px)
- [x] Applied to "Weekly dinners" + "Recipe browser" subheaders on Meals
- [x] Body text and dense data (lists, batteries, light status) stay system sans for legibility
- [x] Type scale updated: H1 = 34px Fraunces / Subhead = 20px Fraunces / Body = 13-15px sans

**Note for HA restart**: `home-hub-fonts.js` only loads after HA restart picks up the new `extra_module_url` entry. For the current session, font was injected via Playwright JS to verify the design before restart. After HA restart, the font will load automatically on all dashboards (only Home Hub uses it via the styles, but the link itself loads globally).

### `/colorize` — Introduce warm accent palette ✅ DONE 2026-04-07
**Strategy**: Sage (`#4A7C59`) = system state / actions / primary engagement. Terracotta (`#C87456`) = "current moment" / temporal awareness. Two colors with clear semantic roles instead of one over-used green.
- [x] Terracotta (`#C87456`) introduced as the "current moment" accent
- [x] Calendar Week View "Today" text changed from green to terracotta (still has subtle warm tile tint `#f9f7f4` background)
- [x] Right Now agenda "TODAY" eyebrow (already terracotta, kept)
- [x] Right Now Tonight's Dinner card "TONIGHT" eyebrow → terracotta (was gray)
- [x] Family page "UP NEXT" eyebrow on all 3 person cards → terracotta (was gray)
- [x] Meals Plan-This-Week day pills: today's pill (Tue when viewing on a Tue) → terracotta border, `#FFF6F1` warm background, terracotta + icon, terracotta day label
- [x] Day-picker popup TODAY badge → terracotta with `#FCE9DE` peach background
- [x] Day-picker popup today card → terracotta border + `#FFF6F1` background
- [x] Petra's avatar already uses `#C87456` (introduced in earlier session)
- [x] Sage (`#4A7C59`) preserved as the action color: nav highlights, sidebar hover, "Plan dinner →" CTA, "Add Recipe" button, `+` plus icons in unfilled day pills, scene chip dots, etc.
- [x] Warm off-white background (`#fbfaf9`) preserved everywhere

**The two-tone discipline reads as intentional**: warm earthy tones for time-aware moments (now/today/tonight/upcoming), cool sage for actionable system state (buttons/nav/active). This is the visual difference between "this dashboard has a point of view" and "this dashboard has too many colors".

### `/clarify` — Rewrite the robotic copy ✅ DONE 2026-04-07
- [x] "Family Members / Select a family member to view their details" → removed (just shows the 3 cards now, no clutter)
- [x] Family page strips home/away presence dots and battery percentages — Bennetts already know where each other are; battery is noise. Cards now focus purely on each person's UP NEXT from their primary calendar.
- [x] Calendar mapping fixed: Ben → `calendar.work_calendar` (was ben_personal); Petra → `calendar.home_calendar`; Toby → `calendar.home_calendar`. Each person sees their own slice instead of a generic family agenda.
- [x] Outlook all-day normalization: `home_hub_fetch_upcoming_events` now detects midnight-to-midnight timed events (Outlook's encoding for all-day) and converts them to `all_day: True` with YYYY-MM-DD start/end. Means Ben's "Out of office" multi-day vacation now displays as "Through Apr 13" instead of "Thu · 12:00 AM".
- [x] Empty-state copy on person cards: friendly fallbacks ("No work events" / "A quiet day at home") instead of robotic "Nothing scheduled".
- [x] Date display improved: events more than 6 days out show "Apr 14 · 2:00 PM" instead of "Tue · 2:00 PM" (eliminates confusion when today is also a Tuesday).
- [x] Meals banner text:
  - empty → "Pick this week's dinners from the recipes below ↓"
  - partial → "N more to go for the week"
  - full → "Week's planned. Time to make the grocery list →"
- [x] Sidebar weather widget condition text bug: `partlycloudy` → "Partly cloudy" (was "Partlycloudy" with no space). Same condMap pattern as Right Now hero.
- [x] All "Coming Soon" placeholders already removed in Phase 1
- [x] Live greeting copy already friendly ("Good morning/afternoon/evening/Up late/Good night")

### `/delight` — Add personality moments ✅ DONE 2026-04-07
- [x] Created shared `hh-pulse` and `hh-fade-in` keyframes in `home-hub-fonts.js` (loaded globally via `extra_module_url`). Also includes a `prefers-reduced-motion` override to disable for accessibility.
- [x] **Person card hover lift**: cards translateY(-3px) on hover with a softer multi-stop shadow, snappy 0.25s `cubic-bezier(0.2, 0.9, 0.3, 1.2)` ease. `:active` adds a subtle press (translateY(-1px) + scale(0.99)).
- [x] **Room card hover lift**: same lift treatment via card_mod, applied through ha-card selector.
- [x] **Scene chip press feedback**: chips warm to terracotta on hover (`#FFF6F1` bg + terracotta border) and snap-press on tap (scale 0.94, `#FCE9DE` deeper bg). Confirms the user that the tap was registered.
- [x] **TODAY eyebrow pulse**: Right Now agenda's "TODAY" label now has a small terracotta dot that pulses outward every 2.4 seconds (very subtle — the kind of motion you only notice if you watch for it). Quietly draws the eye to the most relevant section without being demanding.
- [x] **Outlook event color**: Added `work_calendar` to the calColors map (purple `#9333EA`) so Ben's work events get a distinct dot in the Right Now agenda.

**Why hover-lift over click-flash**: This is a kitchen tablet that primarily takes touch. `:hover` doesn't fire on touch devices, but `:active` does — and the press feedback is the more important interaction for an iPad. Hover lift is a desktop nicety; press feedback is the touch substance.

**Why pulse over flash**: Continuous subtle motion communicates "this is the current/now" without being attention-grabbing the way a flashing color or sliding banner would. It's the dashboard equivalent of a quiet hum vs. an alarm.

---

## Phase 4 — Final Pass

### `/polish` ✅ DONE 2026-04-07
- [x] Visual sweep across all 6 main views (Right Now, Rooms, Calendar, Tasks, Meals, Devices, Family) + Ben subpage
- [x] Updated `CLAUDE.md` "What we changed" section with full Phase 1-3 history, terracotta tokens, Fraunces font reference, and the new files (`right_now.yaml`, `home-hub-fonts.js`)
- [x] **Caught and fixed YAML indentation trap on Family page**: After adding `card_mod:` for hover lift to `home_hub_person_card`, the `grid:` and `custom_fields:` blocks ended up nested inside `card_mod:` instead of `styles:`. Symptom: Ben's avatar rendered off-center because button-card fell back to its default 3-column auto-sized grid (where shorter content = narrower content column). Petra/Toby looked fine because their longer event titles claimed more column space. Fix: rearranged blocks so `card_mod:` comes BEFORE `styles:` and `grid:` + `custom_fields:` are properly under `styles:`. Saved as memory.
- [x] Person card empty fallback message wired ("No work events" / "A quiet day at home")
- [x] Outlook all-day normalization (Phase 2 cleanup) and date display improvement (Phase 3 clarify) verified together — Ben's "Out of office" multi-day event now shows correctly on both Right Now ("Until Mon") and Family ("Through Apr 13" or next timed event "Apr 14 · 2:00 PM Diane Carota")
- [x] All visual checks passing on Right Now, Rooms, Calendar, Tasks, Meals, Devices, Family
- [ ] Re-run `/critique` to measure score lift — *deferred to user*
- [ ] **Note for HA restart**: `home-hub-fonts.js` and the kiosk-mode JS only get picked up by `extra_module_url` after HA restart. The current Playwright session has them injected manually. After restart, fonts/animations load automatically. The configuration was committed and is in place.

**Final state**: Dashboard transformed from "Functional but unrefined" (18/40) into a distinctive, warm, editorial kitchen display with:
- Big Fraunces serif headers across all 6 views
- Disciplined two-color palette (sage = action, terracotta = "now")
- Glance-first Right Now landing with hero clock + greeting + tonight's dinner + agenda
- Family page with rich per-person cards driven by each person's actual primary calendar (Ben→work, Petra/Toby→home)
- Subtle hover/press animations and a quiet pulse on the TODAY eyebrow
- Outlook all-day event normalization
- Friendly, human copy throughout

---

## Phase 5 — Coherence (close the AI-slop seams)

**Goal**: After Phase 1-4 the dashboard scored 24/40. /critique flagged two P0 issues that broke the editorial direction even though everything else was landing: the calendar's repeating multi-day events and the leftover Material-UI icon palette on Rooms/Devices/Family that didn't sit in the warm Editorial Kitchen system. This phase fixes both.

### `/clarify` — Calendar refactor ✅ DONE 2026-04-07
- [x] **Multi-day repetition fixed.** Set `multiDayMode: single` on `custom:week-planner-card` so multi-day events render once on the start day instead of repeating across every cell. "ben - spring break" was 7 cells across the week → 1 cell. Same for "Toby spring break."
- [x] **week-planner-card config bug workaround**: the card source reads `e._multiDayTimeFormat` (with underscore prefix) instead of `e.multiDayTimeFormat` — set the config key with the underscore to actually apply the format. Documented in the YAML comment.
- [x] **12-hour AM/PM format everywhere.** Calendar week + month views now use `timeFormat: "h:mm a"` to match the Right Now clock and hourly forecast.
- [x] **"Entire day" prefix dropped** via `texts.fullDay: " "` override.
- [x] **Date metadata quieted.** Times render as small uppercase gray (`text-transform: uppercase, font-size: 10px, color: #9CA3AF`) so the title gets visual priority.
- [x] **Title clamping.** `-webkit-line-clamp: 2` truncates long titles cleanly instead of pushing cells to absurd heights.
- [x] **Day labels reformed.** Dropped redundant relative labels ("Yesterday", "Tomorrow", "Thursday", "Friday") next to the day numbers via `.container .day .date .text { display: none; }`. Today gets a single dedicated `TODAY` terracotta eyebrow under the number via `::after` pseudo-element. One source of "now" signaling instead of two.
- [x] **Right Now agenda — present-tense labels.** "Until Mon" → "Through Mon" in `home_hub_right_now_main`.
- [x] **Right Now agenda — raw bullet stripping.** Calendar event titles like `"Stay at Misty Mountain Chalet- Pets•EV•Trails•Views•2acres"` (Outlook metadata leak) now strip to `"Stay at Misty Mountain Chalet"`. Regex matches a dash-prefixed segment with bullet runs only — leaves normal titles like `"ben - spring break"` intact.
- [x] **Right Now agenda — title overflow.** Added `white-space: nowrap; overflow: hidden; text-overflow: ellipsis` to the title cell so long titles ellipsis-truncate cleanly.

### `/colorize` — Unified warm icon palette ✅ DONE 2026-04-07

**The 6-color editorial palette** (every color sits in the warm spectrum, no blues/purples/teals):

| Slot | Hex | Use |
|---|---|---|
| Sage | `#4A7C59` | Living Room, batteries, tablets, system primary action |
| Terracotta | `#C87456` | Front House, phones, birthdays, Petra avatar, "current moment" |
| Honey | `#B89254` | Kitchen, both printers (food/appliance warmth) |
| Taupe | `#8E7065` | Bedroom, work calendar dot |
| Clay | `#9A6B47` | Toby's Room, Toby avatar, Toby school tile |
| Olive | `#6E8E4D` | Outside, ben_personal calendar dot |
| Dusk indigo | `#3D3654` | Hourly forecast night blocks (was harsh `#111`) |

**Touched:**
- [x] **Room cards (6):** retinted Front House (was `#488cd0` blue → terracotta), Living Room (was `#a386d7` purple → sage), Kitchen (`#5aa287` green → honey), Bedroom (`#5aa287` → taupe), Toby's Room (`#f4b143` → clay), Outside (`#549f82` → olive). Plus updated all the room popup `mushroom-title-card` border-left accent colors to match.
- [x] **Tinted tile backgrounds.** The room icon tile now derives its background from the room color at 14% alpha (`rgba(r, g, b, 0.14)`) instead of being a uniform `#f8f8f6`. Each room gets its own warm tile, and the icon stays legible without fighting low-contrast strokes. Also bumped icon to 28px with stroke-width 2.25 for stronger presence.
- [x] **Device cards (6):** phones (iPhone, Pixel 10) → terracotta, tablets (Small iPad, Big iPad) → sage, both printers (Brother + Centauri Carbon) → honey, batteries → sage. Default `device_color` fallback in `home_hub_device_card` template also updated from `#a386d7` purple to `#4A7C59` sage.
- [x] **Family avatars:** Ben already sage, Petra already terracotta — Toby switched from blue `#3B82F6` to clay `#9A6B47` (matches his room and his school tile).
- [x] **Toby's Corner — School tile:** clay tile + clay icon (was blue). Other tiles (Swimming/Hockey/I'm Bored) intentionally kept their semantic colors — water=cyan, hockey=red, play=orange — kid-friendly is a feature.
- [x] **Right Now agenda calendar dots:** updated `calColors` map — `home_calendar` stays sage, `birthdays_anniversaries` already terracotta, `ben_personal` blue → olive, `work_calendar` purple → taupe.
- [x] **Calendar week + month views:** `birthdays_anniversaries` calendar color in week-planner-card config changed from purple `#9333EA` to terracotta `#C87456`. Legend dot reflects this.
- [x] **Hourly forecast night blocks:** the `lovelace-hourly-weather` card defines color variables on `.main` inside `weather-bar`'s nested shadow root, which card-mod can't reach from outside. Added a JS patcher to `home-hub-fonts.js` that walks the DOM, finds every `weather-bar` element, and injects a `<style>` tag into its shadow root with warm overrides (clear-night → `#3D3654`, cloudy → `#B6B0A2`, partlycloudy → `#C6D8E8`, sunny → `#F5C57F`). Runs on load + every 1.5s to catch newly mounted elements.

**The "more saturation in the lookup, less in the palette" rule** — when picking these colors I started from the existing sage and terracotta and added 4 siblings that all sit in the same low-saturation warm-earth family. Each color is distinguishable but they all clearly come from the same paint chip. Walking from one view to another now feels like one designed system instead of a Material UI grab bag.

**Required for iPad pickup**: the new `home-hub-fonts.js` (with the night-block patcher) is browser-cached on the iPad. Either hard refresh once on the iPad (Safari → close tab → reopen), or restart HA so `extra_module_url` re-busts. Without that, the iPad keeps showing black night blocks even though the patch is shipped.

---

## Optional: ADHD-friendly add-ons

Based on Ben mentioning ADHD and his multi-year mission to use automation to make life less challenging. These are *additions* to the action plan, not replacements. Tackle after the core direction lands or weave in as we go.

- [ ] **Time blindness widget** on Right Now: "X hours until [next event]" countdown, plus a slow day-progress bar
- [ ] **One-button brain dump**: giant button on landing page → opens voice note → speech-to-text → appended to a `today.md` doc or a Keep note
- [ ] **"Where was I?"** capture: when entering kitchen (presence sensor), shows the last brain dump from < 10 min ago so an interrupted thought can resume
- [ ] **2-minute timer button** on landing page: tap → 2-minute countdown overlay → "just do it for 2 minutes" task initiation
- [ ] **Hydration reminder** with confirmation: ambient nudge at 10am/2pm/6pm with a "Yes, drank water" tap to clear
- [ ] **Body double mode**: tap "study with me" → ambient sound + visible timer → tracks focus session
- [ ] **First-step-only task display**: instead of a list of 50 todos, show just *one* item — the next action — with "next" button
- [ ] **Routine progress bar**: morning routine and evening routine each with their own progress bar showing completion
- [ ] **"What should I make?"** wheel: spin to randomly pick from this week's planned dinners (decision fatigue killer)

---

## Notes
- Multi-session work. Read this file at the start of each session.
- Memory entry created so future Claude sessions can find this plan.
- If priorities shift, edit this file directly — it's the source of truth.
