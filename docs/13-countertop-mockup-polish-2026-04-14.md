# Countertop Mockup Polish — April 14, 2026

Date: April 14, 2026
Authoring context: Claude Code session against the live Home Assistant Samba mount at `/Volumes/config`, verified via Playwright at `http://192.168.68.114:8123`
Scope: Full QA pass of live Countertop dashboard vs HTML mockup, plus targeted fidelity fixes (excluding Mealie integration)
Status: Complete. All P0/P1 visual fidelity issues resolved and user-verified. Dinner popup Mealie assignment remains the single open functional gap from prior session.

## Purpose

After Phase 6 landed the initial mockup fidelity fixes, several gaps remained between the live Countertop dashboard and the HTML mockup. This session ran a full QA comparison (13 live iPad screenshots vs 13 mockup renders), produced a prioritized fix list, and worked through each non-Mealie issue in order.

The Mealie integration gap was explicitly out of scope. The user flagged it as "a much bigger issue" to handle separately. Everything in this session targets the working-without-Mealie state matching the mockup.

## QA Methodology

The user captured 13 live iPad screenshots (IMG_0167–IMG_0180, skipping 0175) covering every view and popup on the Countertop. Each was paired against the corresponding mockup render in `countertop-screenshots/html-mockup-on-ipad/`. The comparison produced a scorecard grouped by severity:

| View | Live | Mockup | State After Session |
|---|---|---|---|
| Home | IMG_0167 | home.PNG | Match (Mealie gap only) |
| Lights | IMG_0168 | lights.PNG | Ring-centered intentional deviation |
| Lights popup (Front House) | IMG_0169 | — | Temp sensor unavailable (data issue, not code) |
| Shopping popup | IMG_0170 | shopping_popup.PNG | Close X added, underline eliminated |
| Ringing phone toast | IMG_0171 | ringing_popup.PNG | Match |
| Timer blank | IMG_0172 | timer_popup-blank.PNG | Full ring, "Ready" centered inside |
| Timer running | IMG_0173 | timer_popup-action.PNG | Countdown centered inside ring |
| Calendar week | IMG_0174 | calendar_week.PNG | Day-of-week labels shown |
| Toby | IMG_0176 | toby.PNG | Input moved above pills, unified card |
| Toby Manage popup | IMG_0177 | toby_checklist_manage.PNG | Close X added |
| Toby School checklist | IMG_0178 | toby_checklist_popup.PNG | Close X added |
| Dinner popup | IMG_0179 | meals_popup.PNG | Mealie-dependent, deferred |
| Plan Meals | IMG_0180 | meals.PNG | Mealie-dependent, deferred |

## Explicit Constraints Followed

- Mealie integration was not touched in this pass.
- No redesigns — only fidelity adjustments to match existing mockup.
- Ring-centered lights design kept (user-preferred deviation from mockup's top-right lightbulb indicator).
- "Master Bedroom" name kept (deliberate earlier rename from "Bedroom").
- Outside card's GATE/SHED sensor dots kept (useful info the mockup omits).

## Live Targets

The work touched the following live files:

- `/Volumes/config/configuration.yaml`
- `/Volumes/config/scripts.yaml`
- `/Volumes/config/dashboards/countertop/scene_bar.yaml`
- `/Volumes/config/dashboards/countertop/button_card_templates.yaml`
- `/Volumes/config/dashboards/countertop/views/calendar.yaml`
- `/Volumes/config/dashboards/countertop/views/toby.yaml`
- `/Volumes/config/dashboards/popups/countertop_shopping_popup.yaml`
- `/Volumes/config/dashboards/popups/countertop_timer_popup.yaml`
- `/Volumes/config/www/home-hub-fonts.js`

## Detailed Change Log by Task

### Task 1: Timer popup ring centering and full-circle behavior

**Goal.** Match the mockup's large ring with `0:00 READY` or countdown text centered inside. The prior state showed the text above or below a small off-center ring that only drew as a partial arc.

**Root cause.** Two compounding bugs in `simple-timer-card`:

1. The card's SVG has a malformed `viewBox="0 0 64"` (missing fourth value). Without a valid viewBox, circles at `cx=32, cy=32, r=28` render in intrinsic pixel space, making them appear small and off-center inside the larger rendering box.
2. The card's JS computes `stroke-dasharray` dynamically from the attribute `r=28`, yielding a circumference of ~175.929. When earlier attempts overrode `r/cx/cy` via CSS to enlarge the circle, the visual circumference grew but the dasharray stayed at 175.929, so the drawn arc only covered ~34% of the visible ring — the "semi-circle" bug.

**Fix.** Use `zoom: 2.8` on the SVG instead of CSS transforms or attribute overrides. `zoom` scales both the visual rendering AND the layout box, so the internal SVG coordinates stay at their natural `r=28` dimensions and the JS-computed dasharray correctly covers the full circumference. Two side effects handled in the same card_mod:

- Track stroke given explicit light peach color (`#F3DDD0`) so the untouched portion reads as background.
- Prog stroke stays terracotta (`#C87456`).
- `.vstatus` (the one element that holds both the idle "Ready" text and the running countdown) absolute-positioned at 50%/50% of `.vcol` with Fraunces 34px so it overlays the ring center.
- `.vtitle` and `.icon-wrap` hidden.

**Files changed.** `/Volumes/config/dashboards/popups/countertop_timer_popup.yaml`.

**Status.** Verified in both blank and running states.

### Task 2: Scene bar active-scene indicator

**Goal.** Match the mockup where one chip (e.g., Bright) displays filled in terracotta to indicate the currently active scene.

**Approach.** Introduce a lightweight state tracker. No plausible sensor exists for "which scene is active" since scenes only set lights and don't record metadata.

**Added.** New `input_select.countertop_active_scene` helper with options `none / Relax / All Off / Bright / Morning / Good Night`. Default `none` so no chip is initially highlighted.

**Added.** New `script.ct_activate_scene` accepting `scene_name` field. Sets the helper and fans out via a `choose` block to the appropriate scene or script call (scene.turn_on, light.turn_off, script.turn_on).

**Changed.** Every chip in `scene_bar.yaml` now calls `script.ct_activate_scene` with its scene name instead of the individual scene/light/script services.

**Changed.** The `ct_scene_chip` template now reads `states['input_select.countertop_active_scene']`, compares to `variables.chip_label`, and applies terracotta text/icon/border plus peach background when matched. `triggers_update` includes the helper so chips re-render on change.

**Files changed.** `/Volumes/config/configuration.yaml`, `/Volumes/config/scripts.yaml`, `/Volumes/config/dashboards/countertop/scene_bar.yaml`, `/Volumes/config/dashboards/countertop/button_card_templates.yaml`.

**Status.** Verified — manually setting the helper via API highlights the matching chip instantly.

### Task 3: Close X buttons on popups

**Goal.** Match mockup — each popup has a small gray circle X in the top-right.

**Scope.** Added to five popups: Shopping, Toby Manage Checklists, Toby School, Toby Swimming, Toby Hockey.

**Implementation.** Each popup title row converted from single-column grid `"t"` to two-column grid `"t close"` with `1fr auto` columns. The close slot renders an SVG X inside a 30px gray circle with inline `onclick`.

**Critical gotcha.** The close handler cannot use `browser_mod.close_popup` even with `browser_id: 'THIS'` — that service requires the browser to be registered with browser_mod, which Playwright's anonymous browser (and by extension some iPad contexts) may not be. Correct approach: walk the DOM to find the `wa-dialog` element (HA 2026.3's Web Awesome dialog primitive) and call its `requestClose('close')` method. The inline JS becomes:

```js
function f(n){for(var c of n.children||[]){if(c.tagName==='WA-DIALOG')return c;var r=f(c)||(c.shadowRoot&&f(c.shadowRoot));if(r)return r;}return null;}
var d=f(document);
if(d&&d.requestClose)d.requestClose('close');
```

**Files changed.** `/Volumes/config/dashboards/popups/countertop_shopping_popup.yaml`, `/Volumes/config/dashboards/countertop/views/toby.yaml` (four inline popup definitions).

**Status.** Verified — click the X and the dialog closes.

### Task 4: Calendar week view day-of-week labels

**Goal.** Match mockup column headers (e.g., `MON 7`, `TUE 8`, `WED 9 TODAY`).

**Root cause.** Earlier CSS hid `.container .day .date .text` (the day-of-week label element in `week-planner-card`) to keep the display sparse. Mockup shows them.

**Fix.** Show `.date .text` in both week and month views with styling: 10px uppercase, 600 weight, 0.06em tracking, gray (`#9CA3AF`). Today's column gets terracotta override on both `.text` and `.number`. Numbers set to Fraunces 22px for serif consistency with the rest of the dashboard.

**Also removed.** Duplicate `TODAY` indicator — the `::after` content that was added earlier (`content: "Today"`) became redundant once the native `.text` label started showing `Today` on the today column.

**Files changed.** `/Volumes/config/dashboards/countertop/views/calendar.yaml`.

**Status.** Verified — week view shows `YESTERDAY / TODAY / TOMORROW / THURSDAY / FRIDAY / SATURDAY / SUNDAY` column headers with terracotta on Today.

### Task 5: Toby "I'm Bored" unified card

**Goal.** Match mockup where the Pick Something button, input row, and activity pills appear as one continuous card with a single border and shadow.

**Root cause.** Previous implementation stacked three separate cards. The middle card (a `custom:layout-card` wrapping the entities input and Add button) doesn't render its own `ha-card` consistently, so the `card_mod` targeting `ha-card` wasn't taking effect — the middle section appeared to float between the top and bottom cards with a visible break.

**Fix.** Wrap all three sections in `custom:vertical-stack-in-card` (HACS card that collapses nested card backgrounds into a single visual container). Inner cards get their individual borders and shadows removed. The wrapper provides the single rounded border, shadow, and white background.

**Also moved.** The input row from below the pills to above (between Pick Something and the pills), matching mockup order.

**Also removed.** The `icon: mdi:plus-circle` attribute from `input_text.toby_new_activity` so the default entity-row icon doesn't render.

**Files changed.** `/Volumes/config/configuration.yaml` (icon removed from helper), `/Volumes/config/dashboards/countertop/views/toby.yaml` (restructure).

**Status.** Verified — renders as a single card with clean vertical rhythm.

### Task 6: Eliminate text field underline on wa-input

**Goal.** Remove the 1px dark gray horizontal line below the text input in the Shopping List popup and the Toby "Add a new activity" input. The mockup shows clean rounded-border inputs with no underline.

**Root cause.** HA 2026.3 replaced MDC (Material Design Components) with Web Awesome's `wa-input`. MDC-era CSS variables like `--mdc-text-field-idle-line-color` no longer apply. The underline comes from a `::after` pseudo-element on the `.text-field` div inside `wa-input`'s shadow DOM — a built-in Web Awesome focus indicator.

**Fix.** Added a rule to the existing wa-input shadow DOM patcher in `home-hub-fonts.js`:

```js
'.text-field::before, .text-field::after { display:none !important; content:none !important; background:transparent !important; height:0 !important; }'
```

Bumped cache-busting query string from `?v=13` to `?v=14` in `configuration.yaml`'s `extra_module_url` list. Restarted HA so the frontend re-fetches the module (reload_core_config is insufficient; `extra_module_url` only re-evaluates on frontend boot).

**Files changed.** `/Volumes/config/www/home-hub-fonts.js`, `/Volumes/config/configuration.yaml`.

**Status.** Verified in both Shopping and Toby inputs post-restart.

## Technical Discoveries

### `zoom` beats `transform: scale()` for scaling SVGs with dynamic dasharrays

When scaling an SVG whose JS computes `stroke-dasharray` from the circle's attribute radius, CSS `transform: scale()` breaks the math (visual circumference grows but dasharray stays calibrated to the original radius). `zoom` scales the layout box too, so internal coordinates stay aligned with the JS assumptions. `zoom` is non-standard but widely supported in WebKit/Blink.

### HA 2026.3 `wa-dialog` closes via `requestClose('close')`

`browser_mod.close_popup` requires a registered browser_id. For unregistered contexts (and to be portable across iPad Safari and Playwright), walk the DOM to find `wa-dialog` and call its `requestClose('close')` method directly. This also works from inline onclick handlers where `fire-dom-event` is unreliable.

### `vertical-stack-in-card` for visually unified multi-card sections

When three cards need to render as one (Pick Something + input + pills), standard stacks leave visible seams because each card renders its own `ha-card` with border/shadow. `custom:vertical-stack-in-card` (HACS) wraps children in a single container and suppresses their individual chrome. Inner children should set their own `background: none; border: none; box-shadow: none` to let the wrapper's styling show through.

### `extra_module_url` version bumps require HA restart

Updating the `?v=N` query string on a file in `extra_module_url` does not take effect via `homeassistant.reload_core_config`. The frontend only re-evaluates `extra_module_url` at bootstrap. Restart HA after editing `home-hub-fonts.js` (or similar) to pick up the new version. iPad WKWebView may also require closing/reopening the dashboard tab.

## Files Added or Materially Changed

### Added

- `input_select.countertop_active_scene` helper in `configuration.yaml`
- `script.ct_activate_scene` in `scripts.yaml`

### Materially changed

- `/Volumes/config/configuration.yaml` (helper added, `toby_new_activity` icon removed, `home-hub-fonts.js` cache bump)
- `/Volumes/config/scripts.yaml` (new scene script)
- `/Volumes/config/dashboards/countertop/scene_bar.yaml` (chips call new script)
- `/Volumes/config/dashboards/countertop/button_card_templates.yaml` (`ct_scene_chip` active-state logic)
- `/Volumes/config/dashboards/countertop/views/calendar.yaml` (day-of-week labels, duplicate TODAY removed, Fraunces numbers)
- `/Volumes/config/dashboards/countertop/views/toby.yaml` (I'm Bored unified card, input row reorder, close X on four popups)
- `/Volumes/config/dashboards/popups/countertop_shopping_popup.yaml` (close X)
- `/Volumes/config/dashboards/popups/countertop_timer_popup.yaml` (ring centering via zoom)
- `/Volumes/config/www/home-hub-fonts.js` (text-field pseudo-element underline hider)

## User-Verified Results

The user confirmed on the iPad:

- Timer popup shows a proper full ring with centered countdown in both blank and running states
- Scene bar indicates the active scene correctly
- Close X buttons on Shopping and Checklist popups dismiss the dialog
- Calendar week view day labels visible and terracotta Today highlight clean
- Toby's I'm Bored section renders as a single unified card
- Dark line under both text inputs eliminated

## Remaining Open Items

- **Dinner popup meal assignment from iPad tap.** The popup opens and the recipe cards render, but the tap-to-assign flow does not commit the selected meal. This was already a known gap from Phase 6 and remains deferred to a separate Mealie-focused session.
- **Front House popup temperature row shows `--°F`.** The template reads `sensor.living_room_temp_temperature`, which is currently `unavailable` (Zigbee sensor offline or battery). The template handles the unavailable state correctly — this is a hardware issue, not a code issue.

## Recommended Next Follow-Up

The next pass should be the Mealie integration session that was explicitly deferred here. The dinner popup shell is stable, the recipe cards render, the assignment action is the remaining functional gap. That work should also cover the Plan Meals view's empty day slots and the home page's "This Week's Meals" counter.
