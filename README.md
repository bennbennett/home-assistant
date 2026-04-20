# Home Assistant Configuration for Claude Code

This directory contains your Home Assistant configuration for easy access with Claude Code.

## Quick Start

### Recommended Login Process
The simplest way to connect Claude to your Home Assistant:

```bash
cd /Users/bbennett/Documents/25_PERSONAL-Environment/home-assistant
source .env
export HASS_URL HASS_TOKEN
```

Then verify the connection:
```bash
curl -s -H "Authorization: Bearer $HASS_TOKEN" $HASS_URL/api/ | python3 -m json.tool
```

You should see: `{"message": "API running."}`

### Using Helper Functions
After loading the environment, you can use the helper script:

```bash
./tools/hass-setup.sh test      # Test connection
./tools/hass-setup.sh summary   # Get entity summary
./tools/hass-setup.sh states    # Get all states
```

### Alternative: Load Everything at Once
This will load the environment AND test the connection:
```bash
cd /Users/bbennett/Documents/25_PERSONAL-Environment/home-assistant && source .env && export HASS_URL HASS_TOKEN && ./tools/hass-setup.sh test
```

## What's Included

- **`.env`** - Your Home Assistant credentials and configuration
- **`tools/hass-setup.sh`** - Helper script that loads environment variables and provides useful functions
- **`README.md`** - This file

## Configuration Details

- **Home Assistant URL:** http://192.168.68.114:8123 (local LAN) / http://100.116.131.121:8123 (Tailscale, from anywhere)
- **Token Name:** Claude MCP
- **Location:** Home (America/Los_Angeles)
- **Version:** 2026.4.3

## Helper Script Usage

After sourcing the setup script, you can use these commands:

### Test Connection
```bash
./tools/hass-setup.sh test
```

### Get Entity Summary
```bash
./tools/hass-setup.sh summary
```

### Get All States
```bash
./tools/hass-setup.sh states
# Or with filter:
./tools/hass-setup.sh states "light"
```

### Get Specific Entity
```bash
./tools/hass-setup.sh entity light.living_room
```

### Call a Service
```bash
./tools/hass-setup.sh service light turn_on '{"entity_id": "light.living_room"}'
```

## Environment Variables

After sourcing the script, these variables are available:
- `$HASS_URL` - Your Home Assistant URL
- `$HASS_TOKEN` - Your authentication token

## Example Commands

### Get Entity Summary (Most Reliable)
```bash
curl -s -H "Authorization: Bearer $HASS_TOKEN" $HASS_URL/api/states | \
python3 -c "
import sys, json
states = json.load(sys.stdin)
domains = {}
for s in states:
    domain = s['entity_id'].split('.')[0]
    domains[domain] = domains.get(domain, 0) + 1
for k in sorted(domains.keys()):
    print(f'{k:20} {domains[k]:4} entities')
print(f'\nTotal: {len(states)} entities')
"
```

### Turn on a light
```bash
curl -X POST -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room"}' \
  $HASS_URL/api/services/light/turn_on
```

### Get all light states
```bash
curl -s -H "Authorization: Bearer $HASS_TOKEN" $HASS_URL/api/states | \
  python3 -c "import sys, json; states=json.load(sys.stdin); lights=[s for s in states if s['entity_id'].startswith('light.')]; print(json.dumps(lights, indent=2))"
```

### Get a specific entity
```bash
curl -s -H "Authorization: Bearer $HASS_TOKEN" $HASS_URL/api/states/light.living_room | python3 -m json.tool
```

### Run an automation
```bash
curl -X POST -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "automation.your_automation"}' \
  $HASS_URL/api/services/automation/trigger
```

## Token Management

Your token is stored in `.env` and has the following details:
- **Created:** January 2025
- **Expires:** 2073 (long-lived token)
- **Name in Home Assistant:** Claude MCP

If you need to create a new token:
1. Go to http://192.168.68.114:8123 (or the Tailscale URL if you're remote)
2. Click your profile (bottom left)
3. Scroll to "Long-Lived Access Tokens"
4. Create a new token
5. Update the `.env` file with the new token

## Troubleshooting

### "401: Unauthorized" Error
This usually means the environment variables aren't properly exported:
1. Make sure you `source .env` first
2. Then explicitly export: `export HASS_URL HASS_TOKEN`
3. Verify they're set: `echo $HASS_TOKEN`

### Helper Script Errors
If `./tools/hass-setup.sh` commands fail:
1. The script loads `.env` automatically, but may not export variables to your current shell
2. Use the direct API commands shown below instead
3. Or explicitly source and export: `source .env && export HASS_URL HASS_TOKEN`

### Connection Failed
1. Check if Home Assistant is running
2. Verify the IP address hasn't changed: `ping homeassistant.local`
3. Check if the token is still valid in Home Assistant
4. Test with: `curl -I $HASS_URL`

### Token Issues
- Tokens can be revoked from Home Assistant UI
- Create a new token and update `.env` if needed
- Verify token works: `curl -H "Authorization: Bearer $HASS_TOKEN" $HASS_URL/api/`

## Security Note

- The `.env` file contains sensitive credentials
- Don't commit this to public repositories
- The token provides full API access to your Home Assistant

## Additional Resources

- [Home Assistant API Documentation](https://developers.home-assistant.io/docs/api/rest)
- [Home Assistant Service Calls](https://www.home-assistant.io/docs/scripts/service-calls/)

---
*Last updated: 2026-04-19*