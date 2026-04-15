# Home Assistant - Claude Code Context

Personal smart home setup (~650 entities) across 4 dashboards on HA 2026.3.0.

## Quick Reference

| Item | Value |
|------|-------|
| **HA URL** | `http://192.168.68.114:8123` (same home & remote via bennett-server Tailscale subnet route) |
| **Credentials** | `. .env` loads `$HASS_URL` and `$HASS_TOKEN` |
| **Config access** | Samba mount at `/Volumes/config/` — `open "smb://192.168.68.114/config"` |
| **Home server** | `/Users/bbennett/Documents/25_PERSONAL-Environment/home-server` (GMKtec — runs Mealie, media, etc.) |
| **Phone** | Pixel 10 (`notify.mobile_app_pixel_10`) |
| **Mealie** | `http://100.68.225.20:9925` (Tailscale — hosted on home server) |
| **3D Printer** | `192.168.68.103` (Elegoo Centauri Carbon) |

## Dashboards

| Dashboard | Default URL | Config root |
|-----------|------------|-------------|
| Home Hub | `/home-hub/right-now` | `/Volumes/config/dashboards/home-hub/` |
| Countertop | `/the-countertop/home` | `/Volumes/config/dashboards/countertop/` |
| iPad | `/lovelace/ipad` | `/Volumes/config/dashboards/tablet.yaml` |
| Mobile | `/mobile-dashboard/home` | `/Volumes/config/dashboards/mobile-redesign-v2.yaml` |

## Commands

```bash
# Load credentials (use dot-sourcing, not 'source')
. .env

# Test connection
curl -s -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/"

# Large responses MUST be saved to file -- piping to python breaks due to buffering
. .env && curl -s -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/states" > /tmp/ha_states.json

# Helper script
./tools/hass-setup.sh test|summary|states|entity|service

# Reload after config changes
curl -X POST -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/services/automation/reload"
curl -X POST -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/services/script/reload"

# Mount Samba (check first)
ls /Volumes/config/ 2>/dev/null || open "smb://192.168.68.114/config"
```

## Where Things Live

**Local repo:**
```
home-assistant/
├── .env                        # HASS_URL, HASS_TOKEN, MEALIE_TOKEN, MEALIE_URL
├── tools/                      # hass-setup.sh, generate_grocery_list.py, import_recipe_pdf.py
├── docs/INDEX.md               # Documentation navigation
├── examples/mockup/            # Design mockups (rooms.png, calendar.png, etc.)
└── history/                    # Session logs
```

**HA config (Samba — `/Volumes/config/`):**

| Path | Purpose |
|------|---------|
| `configuration.yaml` | Main config (entities, extra_module_url, shell_commands) |
| `automations.yaml` | All automations |
| `scripts.yaml` | All scripts |
| `dashboards/home-hub.yaml` | Home Hub root (kiosk_mode config) |
| `dashboards/home-hub/` | Templates, views, decluttering_templates |
| `dashboards/countertop.yaml` | Countertop root |
| `dashboards/countertop/` | Templates, views, scene_bar |
| `dashboards/popups/` | All popup YAML partials |
| `dashboards/tablet.yaml` | iPad dashboard |
| `www/home-hub-fonts.js` | Fraunces loader + JS shadow DOM patchers |
| `www/kiosk-mode/kiosk-mode.js` | Hides HA chrome (manual install, not HACS) |
| `scripts/assign_meal.sh` | Mealie slug→UUID mealplan assignment |

**Related project:** Home server config lives at `/Users/bbennett/Documents/25_PERSONAL-Environment/home-server` — the GMKtec box that runs Mealie, media services, and other self-hosted infrastructure. Refer to that repo when debugging Mealie connectivity, server-side scripts, or Docker services.

## Home Hub Architecture

Two-layout sidebar (198px expanded / 64px collapsed) via `input_boolean.sidebar_collapsed`. Each view: `type: panel` → `vertical-stack` → two conditional `layout-card` grids:
```
conditional → layout-card (grid: 198px 1fr, gap 16px) → [sidebar_expanded, <view>_main]
conditional → layout-card (grid: 64px 1fr, gap 16px) → [sidebar_collapsed, <view>_main]
```

Views (sidebar order): Right Now → Calendar → Tasks → Meals → Rooms → Devices → Family. Subpages: Ben, Petra, Toby.

Key files: `button_card_templates.yaml` (templates), `decluttering_templates.yaml` (sidebars + content).

## Design System

**Editorial Kitchen**: warm-neutral palette, Fraunces serif, glance-first.

| Token | Value |
|-------|-------|
| Page bg / Card bg | `#fbfaf9` / `#FFFFFF` |
| Card | `16px` radius, `1px solid #F3F4F6`, `0 1px 3px rgba(0,0,0,0.05)`, `20px` pad |
| Pills | `22px` radius, `40px` height, `500` weight |
| Sage `#4A7C59` | Action: buttons, nav, primary state |
| Terracotta `#C87456` | Current moment: TODAY, TONIGHT, UP NEXT |
| Honey `#B89254` / Taupe `#8E7065` / Clay `#9A6B47` / Olive `#6E8E4D` | Room & device accents |
| Fraunces | Display font (headers, hero). Body: system-sans |

Room palette: Front House→terracotta, Living Room→sage, Kitchen→honey, Bedroom→taupe, Toby's Room→clay, Outside→olive. Tile bg = icon color at 14% alpha.

## Constraints

- MUST save large API responses to file before parsing -- piping `/api/states` to Python silently truncates
- MUST NOT use `html` or `hass` as variable names in button-card JS templates -- conflicts with built-in scope
- MUST NOT pass SVG markup as YAML variables -- gets HTML-escaped; use icon-key maps in JS
- MUST use `fire-dom-event` (not `call-service` to scripts) for browser_mod popups -- scripts can't target the rendering browser
- MUST transform Mealie responses to flat string-only dicts before firing events -- `datetime.date` and enums produce Python repr strings
- MUST bump `?v=N` on `extra_module_url` AND restart HA after editing `home-hub-fonts.js` -- iPad WKWebView ignores cache-clear notifications
- NEVER auto-send grocery lists -- generate → manual review → explicit Send to Keep
- NEVER show home/away or battery on Family page -- 3-person family, not actionable
- HA 2026.3: `ha-textfield` shadow DOM is now `ha-textfield > ha-input > wa-input`. Patchers targeting `.mdc-*` silently fail -- MUST target `wa-input` classes instead

## Troubleshooting

- **Samba not mounted:** `ls /Volumes/config/ 2>/dev/null || open "smb://192.168.68.114/config"`. Remote: verify Tailscale `--accept-routes` is enabled.
- **401 error:** HA web UI > Profile > Long-Lived Access Tokens > Create new > Update `.env`
- **Dashboard not updating after YAML edit:** HA restart is the bulletproof reload for YAML-mode dashboards

## Skill Routing

ALWAYS invoke matching skills as your FIRST action:
- Bugs/errors → `investigate` | Ship/deploy/PR → `ship` | QA/test → `qa`
- Code review → `review` | Design polish → `design-review` | Architecture → `plan-eng-review`
- Checkpoint/resume → `checkpoint` | Health check → `health`

## More Information

See `docs/INDEX.md` for detailed documentation. See `README.md` for additional API examples.

Last tidy review: 2026-04-13 -- if 30+ days stale, suggest running /claude-md-creator tidy
