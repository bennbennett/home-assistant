# Home Assistant Documentation Index

> Master navigation for all Home Assistant documentation.
> Start with [CLAUDE.md](../CLAUDE.md) for quick reference — it covers credentials, URLs, entity tables, Mealie integration, dashboard patterns, and common tasks.

## Document Map

| Document | Purpose |
|----------|---------|
| [CLAUDE.md](../CLAUDE.md) | Quick reference: URLs, credentials, entities, integrations, dashboard patterns, common API tasks. Start here. |
| [HOME_ASSISTANT_DOCS.md](../HOME_ASSISTANT_DOCS.md) | Longer-form reference: system tour and command catalog. |
| [dashboards/README.md](../dashboards/README.md) | Dashboard layout, card templates, popup files. |
| [tools/README.md](../tools/README.md) | Helper scripts (`hass-setup.sh`, `monitor_lights.py`, `generate_grocery_list.py`, `import_recipe_pdf.py`). |
| [history/CHANGELOG.md](../history/CHANGELOG.md) | All notable config changes, reverse-chronological. |
| [11-home-hub-sidebar-debugging.md](11-home-hub-sidebar-debugging.md) | Historical debug log — mostly resolved. |

The planned numbered docs (00–10) never got authored; the content lives in CLAUDE.md, HOME_ASSISTANT_DOCS.md, and the `.claude/rules/*.md` files (auto-loaded by Claude Code via path-glob rules).

## System Summary

| Metric | Value |
|--------|-------|
| **Home Assistant URL** | http://192.168.68.114:8123 (local) / http://100.116.131.121:8123 (Tailscale) |
| **Version** | 2026.4.3 |
| **Total Entities** | ~650 |
| **Automations** | 25 total (21 enabled) |
| **Timezone** | America/Los_Angeles |

## Related Resources

- **Tools**: See [tools/README.md](../tools/README.md)
- **Examples**: See [examples/](../examples/)
- **Changelog**: See [history/CHANGELOG.md](../history/CHANGELOG.md)

## File Locations

### Local (this repository)
```
home-assistant/
├── CLAUDE.md          # Quick reference (start here)
├── .env               # Credentials
├── docs/              # This documentation
├── tools/             # Helper scripts
├── examples/          # Code snippets
└── history/           # Logs and changelog
```

### Home Assistant Config (via Samba)
```
/Volumes/config/
├── automations.yaml         # Automations
├── configuration.yaml       # Main config
├── adaptive_lighting.yaml   # Color temp settings
├── lights.yaml              # Light templates
├── dashboards/              # Dashboard files
│   ├── tablet.yaml          # Original iPad dashboard
│   ├── home-hub.yaml        # Home Hub dashboard (new)
│   ├── home-hub/            # Home Hub templates & views
│   ├── views/rooms.yaml
│   └── button_card_templates.yaml
├── www/
│   └── kiosk-mode/          # Kiosk mode JS (hides HA chrome)
└── .storage/                # Integration configs
```

---
*Last updated: April 19, 2026*
