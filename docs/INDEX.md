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
| 12 | [Countertop Live Remediation (Apr 11, 2026)](12-countertop-live-remediation-2026-04-11.md) | Codex session log: Phase 4 interaction remediation on `/Volumes/config` live. 7/8 tasks complete; dinner popup still broken |
| 13 | [Countertop Mockup Polish (Apr 14, 2026)](13-countertop-mockup-polish-2026-04-14.md) | QA pass + fidelity fixes: timer ring centering, scene bar active state, close-X buttons, calendar day labels, I'm Bored unified card, wa-input underline removed |

## System Summary

| Metric | Value |
|--------|-------|
| **Home Assistant URL** | http://192.168.68.114:8123 (same URL home & remote — remote via bennett-server Tailscale subnet route) |
| **Version** | 2026.3.0 |
| **Total Entities** | ~650 |
| **Automations** | 25 total (21 enabled) |
| **Timezone** | America/Los_Angeles |

## Related Resources

- **Tools**: See [tools/README.md](../tools/README.md)
- **Examples**: See [examples/](../examples/)
- **Changelog**: See [history/CHANGELOG.md](../history/CHANGELOG.md)

## File Locations

**Single repo** (dev assets + HA config unified). HA Git Pull add-on syncs from GitHub to `/config` on the server.

```
home-assistant/
├── CLAUDE.md                # Quick reference (start here)
├── .env                     # Credentials (not tracked)
├── configuration.yaml       # Main HA config
├── automations.yaml         # All automations
├── scripts.yaml             # All scripts
├── dashboards/
│   ├── home-hub.yaml        # Home Hub root
│   ├── home-hub/            # Home Hub templates & views
│   ├── countertop.yaml      # Countertop root
│   ├── countertop/          # Countertop templates & views
│   ├── popups/              # All popup YAML partials
│   └── tablet.yaml          # iPad dashboard
├── www/
│   ├── home-hub-fonts.js    # Fraunces loader + shadow DOM patchers (v15)
│   └── kiosk-mode/          # Kiosk mode JS (hides HA chrome)
├── docs/                    # This documentation
├── tools/                   # Helper scripts
├── examples/                # Mockups and debugging screenshots
└── history/                 # Logs and changelog
```

Deploy: edit locally, `git push`, Git Pull syncs to HA, restart HA for config changes.

---
*Last updated: April 17, 2026*
