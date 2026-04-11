# Countertop Live Remediation Changelog

Date: April 11, 2026  
Authoring context: Codex session working directly against the live Home Assistant Samba mount at `/Volumes/config`  
Scope: Countertop dashboard interaction fixes and targeted visual cleanup  
Status: Partially complete, with one known functional gap still open in the dinner popup flow

## Purpose

This document records the live remediation work performed on the Countertop dashboard after earlier passes left several interactions broken or only partially implemented. The intent of this pass was not to redesign the dashboard, but to finish the interaction model in the touched areas, preserve the calm visual direction, and keep the implementation aligned with the existing Home Assistant structure.

The work was performed against the live Home Assistant configuration files under `/Volumes/config`, not the repository copies in the local workspace. That distinction matters because the repo copy was explicitly not treated as authoritative for this pass.

## Live Targets

The work focused on the following live files:

- `/Volumes/config/dashboards/countertop/views/home.yaml`
- `/Volumes/config/dashboards/countertop/views/toby.yaml`
- `/Volumes/config/dashboards/countertop/views/meals.yaml`
- `/Volumes/config/dashboards/countertop/views/calendar.yaml`
- `/Volumes/config/dashboards/countertop/button_card_templates.yaml`
- `/Volumes/config/dashboards/countertop/scene_bar.yaml`
- `/Volumes/config/dashboards/resources.yaml`
- `/Volumes/config/dashboards/popups/countertop_shopping_popup.yaml`
- `/Volumes/config/dashboards/popups/countertop_tonight_meal_popup.yaml`
- `/Volumes/config/dashboards/popups/countertop_timer_popup.yaml`
- `/Volumes/config/dashboards/popups/countertop_hourly_weather_popup.yaml`
- `/Volumes/config/www/home-hub-fonts.js`
- `/Volumes/config/scripts.yaml`
- `/Volumes/config/automations.yaml`
- `/Volumes/config/configuration.yaml`

## Explicit Constraints Followed

The following constraints were carried through the implementation:

- Toby Manage remained a popup and was not inlined onto the Toby page.
- The page was kept visually calm. The work aimed to reduce default Home Assistant chrome, not add new complexity.
- Lights were not touched.
- Calendar architecture was not redesigned.
- Meals page architecture was not restructured.
- Checklist popups were not migrated wholesale to Bubble Card.
- Browser Mod remained the default popup plumbing.
- Bubble Card was not introduced in this pass.
- The timer source of truth remained `timer.kitchen_timer`.
- Wake lock was treated as best-effort only and was not allowed to block completion.

## Mock / Screenshot References Used

The remediation was driven by the live-versus-mock comparison set supplied for the Countertop dashboard:

- `IMG_0130` live Home vs `IMG_0121` mock Home
- `IMG_0131` live Lights vs `IMG_0122` mock Lights
- `IMG_0132` live Shopping popup vs `IMG_0123` mock Shopping popup
- `IMG_0133` live Find Phone feedback vs `IMG_0124` mock feedback
- `IMG_0134` live Timer popup vs `IMG_0125` mock timer popup
- `IMG_0135` live Calendar vs `IMG_0126` mock Calendar
- `IMG_0136` live Toby vs `IMG_0128` mock Toby
- `IMG_0137` live Checklist popup vs `IMG_0129` mock checklist popup
- `IMG_0138` live Meals vs `IMG_0127` mock Meals
- `IMG_0139` mock target for Home dinner popup
- `IMG_0140` mock target for Toby Manage popup
- `IMG_0141` mock target for live timer state and running popup
- `IMG_0142` mock target for hourly weather popup

## High-Level Outcome

The final state of the pass was:

- Shopping popup: working
- Toby Add Activity input: working
- Weather popup: working
- Timer popup: working
- Toby Manage popup and seasonal visibility wiring: working
- Hockey seasonal controls and checklist: restored
- Dinner popup: popup shell exists, but the assignment action is still not working
- Find Phone feedback: implementation changed to toast-based feedback, but not re-verified in the last live test cycle to avoid disturbing the target device

## Architectural Decisions

Several implementation decisions changed over the course of the work.

### 1. Native Lovelace controls were chosen over raw popup HTML

The original failures on iPad Safari were clustered around controls rendered as custom HTML inside `button-card` JavaScript templates, especially in Browser Mod popups. These controls could look correct but fail on one or more of the following:

- tap focus reliability
- soft keyboard behavior
- spacebar behavior
- button action dispatch

For that reason, the shopping input, Toby Add Activity input, and dinner assignment controls were progressively moved away from raw HTML controls and toward native Lovelace controls such as:

- `entities` cards rendering `input_text` / `input_select`
- standard service buttons via `custom:button-card`
- `layout-card` for the visual shell around native controls

The visual shell remained custom, but the interaction surfaces were moved onto Home Assistant-native control paths.

### 2. Browser Mod remained the popup shell

Browser Mod stayed the popup infrastructure for:

- Shopping List
- Dinner popup
- Toby Manage
- Timer popup
- Hourly Forecast

This preserved the existing popup model and avoided introducing a second popup system where it was not necessary.

### 3. Bubble Card was not used

Bubble Card was available, but it was not used in this pass. The implementation goals could be met with Browser Mod plus existing custom cards without introducing a new shell layer.

### 4. The timer popup moved from custom logic to `simple-timer-card`

The timer popup was initially kept on a more custom rendering path and later trialed with `circular-timer-card`. That card could display a timer state but did not maintain its own live update loop, which caused a specific failure mode:

- the popup could reopen showing a correct static snapshot
- the ring and countdown did not animate live while the popup was open

The popup timer renderer was therefore switched to `simple-timer-card`, which does maintain its own update interval and can reliably animate the timer state while the popup is open.

The Home tile itself remained custom and continued using frontend-driven countdown text.

## Detailed Change Log by Task

## Task 1: Home Meals Card Popup

### Goal

The Home right-rail meals card needed to open a popup, not navigate, and the popup needed to support assigning a recipe to tonight using the existing meal infrastructure.

### What changed

- The Home meals interaction was changed away from dead or incorrect navigation behavior and routed to a Browser Mod popup.
- A dedicated dinner popup partial was created at:
  - `/Volumes/config/dashboards/popups/countertop_tonight_meal_popup.yaml`
- A wrapper script was added / updated:
  - `/Volumes/config/scripts.yaml`
  - `countertop_assign_meal_to_tonight`

### Script behavior

`countertop_assign_meal_to_tonight` was implemented to:

- determine today via `now().strftime('%A')`
- set `input_select.meal_day_selector` to today
- set `input_select.recipe_selector` to the requested recipe
- call the existing `assign_meal_to_day` flow

It was later updated so that if a `recipe_name` is not explicitly passed, it falls back to the current value of `input_select.recipe_selector`. That change was needed to support a more native selector-driven popup instead of brittle HTML choice buttons.

### Why the popup was rebuilt

The first popup approach attempted to use more custom tappable candidate controls. The visual shell was acceptable, but the tap behavior remained unreliable in live testing. To stabilize the interaction path, the popup was rebuilt around:

- a current-tonight summary block
- a native `input_select.recipe_selector`
- an explicit `Assign To Tonight` action button

### Current result

- The popup itself opens.
- The popup visually reads in the intended direction.
- The dinner assignment action is still not working correctly as of the last live test.

### Current status

Not complete. This remains the one known open gap from the remediation pass.

## Task 2: Toby Manage Popup

### Goal

Manage needed to remain a popup, and the seasonal booleans inside the popup needed to control what appears on the Toby page.

### What changed

- Toby Manage remained popup-only.
- The popup booleans were wired to page visibility.
- `season_school` now controls visibility of the School checklist card.
- `season_swimming` now controls visibility of the Swimming checklist card.
- Hockey was restored after the user noted it had been removed.

### Hockey restoration

The implementation was revised so that Hockey was not left as a dead or removed season option.

Restoration work included:

- reintroducing `input_boolean.season_hockey` into the Toby Manage popup
- adding a visible Hockey checklist section back onto the Toby page
- adding Hockey icon mappings to the checklist template layer in:
  - `/Volumes/config/dashboards/countertop/button_card_templates.yaml`

### Empty state

A calm empty state was added so that if all seasonal sections are hidden, the page does not appear broken or blank.

### Current result

- Manage remains a popup.
- School, Swimming, and Hockey can be visibility-gated.
- The page does not gain new permanent clutter.

### Current status

Functionally complete, based on the live feedback received in this round.

## Task 3: Shopping List Popup Polish

### Goal

The shopping popup needed to read like part of the Countertop dashboard rather than a Home Assistant admin dialog. It also needed a reliable input field and Add button on iPad.

### What changed

- The Browser Mod popup shell was kept.
- The visible HA dialog header was hidden.
- The popup stayed narrow and centered.
- The title was rendered as a serif in the popup content.
- The input area was rebuilt to use native Lovelace controls instead of brittle custom HTML controls.

### Final structure

The final shopping popup in:

- `/Volumes/config/dashboards/popups/countertop_shopping_popup.yaml`

uses:

- a title `button-card`
- a `layout-card` row
- an `entities` card containing `input_text.add_to_list_item`
- a native Add button calling `script.ct_add_to_shopping_list`
- a centered “View full list ->” link-style action

### Shared styling support

`/Volumes/config/www/home-hub-fonts.js` was extended to patch `ha-textfield` shadow DOM so the input field could be styled without HA-native form chrome:

- no underline
- no helper line
- no helper counter
- no leading icon
- custom border, radius, fill, and focus treatment

### Live verification result

The user confirmed:

- the shopping popup works
- the Add action works
- the field supports normal typing

### Current status

Complete.

## Task 4: Toby Add Activity Inline Field Polish

### Goal

The Add Activity control needed to remain inline on the Toby page while losing the HA-native field appearance.

### What changed

- The inline location was preserved.
- The control row was visually merged into the bored card area.
- The raw custom HTML input approach was replaced with native Lovelace controls inside a custom shell.

### Final structure

In:

- `/Volumes/config/dashboards/countertop/views/toby.yaml`

the Add Activity row now uses:

- `custom:layout-card` for shell layout
- an `entities` card containing `input_text.toby_new_activity`
- a native Add button calling `script.toby_add_activity`

The shared input patch in `home-hub-fonts.js` provides the styling that removes the default HA field chrome.

### Live verification result

The user confirmed:

- the field accepts text
- the spacebar now works
- the Add button works

### Current status

Complete.

## Task 5: Find Phone Feedback

### Goal

Keep `script.ring_iphone` but replace modal-style feedback with a real transient toast/snackbar.

### What changed

In:

- `/Volumes/config/dashboards/countertop/views/home.yaml`

the Find Phone action was changed to use a Browser Mod sequence:

- call `script.ring_iphone`
- show a Browser Mod notification

In:

- `/Volumes/config/www/home-hub-fonts.js`

the Home Assistant / Browser Mod toast host was patched so the feedback appears as a top-center terracotta toast rather than a default snackbar in the usual location.

### Intended effect

- no dimming overlay
- no modal shell
- immediate feedback
- automatic dismissal

### Live verification result

This was not re-verified during the final testing round because the target phone was unavailable for disturbance.

### Current status

Implemented, but last-round live confirmation is still outstanding.

## Task 6: Timer Function and Popup Shell

### Goal

The timer needed to visibly work from both the Home tile and the popup. The popup needed a live countdown, a draining terracotta ring, and working Pause / Cancel behavior. The mounted iPad also needed an audible completion alert.

### What changed on the Home tile

In:

- `/Volumes/config/dashboards/countertop/views/home.yaml`

the Home tile for `timer.kitchen_timer` was kept custom and updated to:

- show active / paused styling
- compute remaining time client-side when possible
- fall back to `remaining` if necessary
- show live countdown text on the tile itself

This preserved the existing Countertop look while making the tile stateful and visibly useful.

### Popup evolution

The timer popup went through multiple implementations:

1. Existing custom timer popup model
2. More custom HTML / custom-card approach
3. `circular-timer-card`
4. Final switch to `simple-timer-card`

The decisive issue was that `circular-timer-card` could render a correct timer position but not maintain a live countdown animation in the popup. It did not appear to run an internal update loop for the active timer state in the way the use case required.

`simple-timer-card` does maintain an internal update interval and therefore became the final popup renderer.

### Final popup structure

In:

- `/Volumes/config/dashboards/popups/countertop_timer_popup.yaml`

the popup now contains:

- a custom serif title
- `custom:simple-timer-card` bound to `timer.kitchen_timer`
- circular timer display
- drain-style progress mode
- manual preset grid below
- conditional Pause / Resume and Cancel buttons

### Resource changes

To support the final popup renderer, a resource entry was added in:

- `/Volumes/config/dashboards/resources.yaml`

for:

- `/hacsfiles/simple-timer-card/simple-timer-card.js`

`circular-timer-card` remains installed and listed as a resource, but it is no longer the active popup timer renderer.

### Completion alert

In:

- `/Volumes/config/automations.yaml`

an automation was added:

- `countertop_kitchen_timer_finished_alert`

This listens for the `timer.finished` event on `timer.kitchen_timer` and sends an audible critical notification to the mounted iPad.

### Wake lock

In:

- `/Volumes/config/www/home-hub-fonts.js`

best-effort screen wake lock support was added. It is route-gated to Countertop and only requests wake lock while the kitchen timer is active. It releases when:

- the timer is no longer active
- the page is hidden
- the route changes away from the Countertop dashboard

This was implemented as optional enhancement only. If Safari declines or lacks support, the timer still functions normally.

### Live verification result

The user confirmed:

- the timer popup works
- the popup now shows a working timer
- the completion sound works

### Current status

Complete.

## Task 7: Weather Tap Popup

### Goal

Home weather needed to stop being a dead visual block and open an hourly forecast popup using the existing hourly weather strip.

### What changed

- A dedicated hourly forecast popup partial was added at:
  - `/Volumes/config/dashboards/popups/countertop_hourly_weather_popup.yaml`
- The Home header tap action in:
  - `/Volumes/config/dashboards/countertop/views/home.yaml`
  was wired to a Browser Mod popup using that content.

### Styling

The existing warm weather-bar shadow DOM patch in:

- `/Volumes/config/www/home-hub-fonts.js`

was reused so the popup preserved the warm Countertop color treatment instead of default weather card colors.

### Compromise

The preferred target was a weather-only tap hit area. In the final live implementation, the entire Home header became the weather popup trigger. This was accepted as a functional fallback because it removed the dead tap and worked reliably on the iPad.

### Live verification result

The user confirmed:

- tapping opens the popup
- the popup works
- whole-header tap behavior is acceptable for now

### Current status

Functionally complete, with a known refinement opportunity to narrow the tap target later.

## Task 8: Checklist Popup Polish

### Goal

Checklist popups needed to remain stable and readable, with only minor polish rather than a structural migration.

### What changed

The underlying checklist popup architecture was preserved. Minor refinements were made to:

- icon mapping coverage
- divider softness
- consistency with the custom checklist item pattern already in use

No migration to Bubble Card was performed.

### Current status

Stable, with no reported regression from the live testing in this round.

## Shared Frontend Patching

The file:

- `/Volumes/config/www/home-hub-fonts.js`

became the shared frontend patch point for several behaviors that cannot be solved cleanly with standard YAML styling because of nested shadow DOM boundaries.

### Patches present after this pass

- Fraunces font loading
- shared animation keyframes
- hourly weather warm style patch
- Countertop sparse-view vertical centering patch
- Browser Mod / HA toast restyling to top-center
- best-effort wake lock support while `timer.kitchen_timer` is active
- native `input_text` shadow-DOM styling patch for Browser Mod popups and inline controls

### Why this mattered

The Shopping and Toby Add Activity inputs both render through `ha-textfield` shadow roots. Standard `card_mod` styling cannot fully reach these internals. The JS patcher therefore injects styles directly into those shadow roots and does so in a route-gated, repeat-safe way.

## Files Added or Materially Changed

### Added

- `/Volumes/config/dashboards/popups/countertop_hourly_weather_popup.yaml`

### Materially changed

- `/Volumes/config/dashboards/countertop/views/home.yaml`
- `/Volumes/config/dashboards/countertop/views/toby.yaml`
- `/Volumes/config/dashboards/countertop/button_card_templates.yaml`
- `/Volumes/config/dashboards/resources.yaml`
- `/Volumes/config/dashboards/popups/countertop_shopping_popup.yaml`
- `/Volumes/config/dashboards/popups/countertop_tonight_meal_popup.yaml`
- `/Volumes/config/dashboards/popups/countertop_timer_popup.yaml`
- `/Volumes/config/www/home-hub-fonts.js`
- `/Volumes/config/scripts.yaml`
- `/Volumes/config/automations.yaml`

## User-Verified Results at End of Pass

The final live user feedback for this remediation cycle was:

- Shopping popup works
- Spacebar works in Toby Add Activity
- Dinner popup still does not work
- Timer popup now works
- Weather popup works

Additional earlier confirmation in the same cycle indicated:

- Toby Manage popup works
- Hockey needed to be re-enabled, and was restored

## Final State by Requested Reporting Category

### What changed for each task

- Home meals card: popup architecture improved, wrapper script added, still not functionally complete
- Toby Manage: popup-only approach preserved, seasonal visibility now wired to visible page content, Hockey restored
- Shopping popup: popup shell and input control path rebuilt, now functioning
- Toby Add Activity: inline shell retained, native input path substituted, now functioning
- Find Phone: feedback converted from modal-style behavior to transient toast
- Timer: popup renderer switched to `simple-timer-card`, live countdown and completion alert now working
- Weather: popup added and wired, using existing hourly weather strip
- Checklist popups: preserved and lightly refined, no major architecture change

### Which popups stayed on Browser Mod

- Shopping popup
- Dinner popup
- Toby Manage popup
- Timer popup
- Hourly Forecast popup

### Which used Bubble Card

- None in this pass

### Whether the timer stayed custom or switched to `simple-timer-card`

- Home tile stayed custom
- Popup switched to `simple-timer-card`

### Whether wake lock was attempted

- Yes, as best-effort only in `home-hub-fonts.js`

### Remaining limitations from iPad Safari or HA timer behavior

- Browser Mod popup content combined with custom HTML controls proved unreliable on iPad Safari for text input and action dispatch, which is why those controls were moved onto native Lovelace surfaces
- The weather popup is currently triggered by the whole Home header, not a weather-only target
- The dinner popup still has an unresolved functional gap in its assignment flow
- Wake lock support is browser-dependent and cannot be guaranteed on every iPad Safari / HA companion environment

## Verification Notes

The live YAML files were syntax-checked after the remediation edits. The implementation relied on the actual installed HACS resources on disk under:

- `/Volumes/config/www/community/simple-timer-card/`
- `/Volumes/config/www/community/circular-timer-card/`

The final popup timer choice was made after verifying the behavior of those installed assets rather than assuming feature parity from memory.

## Recommended Next Follow-Up

The next pass should focus narrowly on the dinner popup only. The popup shell already exists and the rest of the touched areas are now stable enough that the remaining work can be isolated to:

- confirming the selected recipe value at click time
- validating the wrapper script call path in the popup context
- ensuring the popup either closes or refreshes after assignment

That should be handled as a targeted fix rather than reopening the broader remediation scope.
