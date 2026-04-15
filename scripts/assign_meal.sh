#!/bin/bash
# assign_meal.sh — Look up recipe UUID from slug, create mealplan entry in Mealie.
# Called by HA shell_command.mealie_assign_meal with slug and date as arguments.
# Fix 2026-04-11: Bypasses the broken mealie.set_mealplan HA integration which
# can't get recipe UUIDs from mealie.get_recipes (field not populated).

SLUG="$1"
DATE="$2"
MEALIE_URL="http://100.68.225.20:9925"
# Read token from secrets.yaml (same filesystem, HA container)
TOKEN=$(grep 'mealie_token_header' /config/secrets.yaml | sed 's/.*: *"*//' | sed 's/"*$//')

if [ -z "$SLUG" ] || [ -z "$DATE" ]; then
  echo "Usage: assign_meal.sh <slug> <date>" >&2
  exit 1
fi

# Step 1: Look up recipe UUID from slug
UUID=$(curl -s -H "Authorization: $TOKEN" "$MEALIE_URL/api/recipes/$SLUG" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$UUID" ]; then
  echo "Failed to look up UUID for slug: $SLUG" >&2
  exit 1
fi

# Step 2: Create mealplan entry
curl -s -X POST -H "Authorization: $TOKEN" -H "Content-Type: application/json" \
  -d "{\"date\": \"$DATE\", \"entry_type\": \"dinner\", \"recipe_id\": \"$UUID\"}" \
  "$MEALIE_URL/api/households/mealplans" > /dev/null 2>&1

echo "OK: $SLUG ($UUID) → $DATE"
