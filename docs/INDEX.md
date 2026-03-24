# Home Assistant Documentation Index

> Master navigation for all Home Assistant documentation.
> Start with [CLAUDE.md](../CLAUDE.md) for quick reference.

## Quick Links

| Need | Document |
|------|----------|
| Quick start & common commands | [CLAUDE.md](../CLAUDE.md) |
| API commands & service calls | [02-api-reference.md](02-api-reference.md) |
| Dashboard modifications | [03-dashboard-guide.md](03-dashboard-guide.md) |
| Automation reference | [04-automations.md](04-automations.md) |
| Troubleshooting | [08-troubleshooting.md](08-troubleshooting.md) |

## Document Map

| # | Document | Purpose |
|---|----------|---------|
| 00 | [System Overview](00-system-overview.md) | Architecture, integrations, entity stats |
| 01 | [Getting Started](01-getting-started.md) | Initial setup, credentials, first connection |
| 02 | [API Reference](02-api-reference.md) | curl commands, helper script, service calls |
| 03 | [Dashboard Guide](03-dashboard-guide.md) | iPad dashboard, card templates, popups |
| 04 | [Automations](04-automations.md) | All automations documented |
| 05 | [Integrations](05-integrations.md) | Key integrations (Hue, ZHA, Adaptive Lighting) |
| 06 | [Entities](06-entities.md) | Entity catalog by domain |
| 07 | [Configuration](07-configuration.md) | File structure, Samba access, YAML patterns |
| 08 | [Troubleshooting](08-troubleshooting.md) | Common issues and solutions |
| 09 | [Procedures](09-procedures.md) | Maintenance, backup, token refresh |
| 10 | [Patterns](10-patterns.md) | Reusable solutions (templates, popup patterns) |
| 11 | [Home Hub Sidebar Debugging](11-home-hub-sidebar-debugging.md) | **MOSTLY RESOLVED** - Sidebar layout working; weather content alignment pending |

## System Summary

| Metric | Value |
|--------|-------|
| **Home Assistant URL** | http://192.168.68.114:8123 (local) / http://100.116.131.121:8123 (Tailscale) |
| **Version** | 2026.3.0 |
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
*Last updated: March 2026*
