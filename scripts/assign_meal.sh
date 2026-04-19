#!/bin/bash
# assign_meal.sh — Replace the dinner mealplan entry for a given date.
# Called by HA shell_command.mealie_assign_meal with slug and date as arguments.
#
# Mealie's POST /households/mealplans always *appends* — it never replaces.
# Without this script, re-assigning a meal stacks entries forever and the
# HA sensor ends up with multiple rows per date, breaking the "current meal"
# display. This script deletes any existing dinner entry for the date first,
# then creates the new one. Net effect: one dinner per day, no accumulation.

set -u

SLUG="$1"
DATE="$2"
ENTRY_TYPE="dinner"
MEALIE_URL="http://100.68.225.20:9925"
TOKEN=$(grep 'mealie_token_header' /config/secrets.yaml | sed 's/.*: *"*//' | sed 's/"*$//')

if [ -z "$SLUG" ] || [ -z "$DATE" ]; then
  echo "Usage: assign_meal.sh <slug> <date>" >&2
  exit 1
fi

# Step 1: Delete any existing dinner entries for this date.
# GET /households/mealplans returns items with entryType (camelCase).
EXISTING_IDS=$(curl -s -H "Authorization: $TOKEN" \
  "$MEALIE_URL/api/households/mealplans?start_date=$DATE&end_date=$DATE&perPage=100" \
  | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    for i in d.get('items', []):
        if i.get('entryType') == '$ENTRY_TYPE' and i.get('date') == '$DATE':
            print(i['id'])
except Exception as e:
    sys.stderr.write(str(e))
")

for ID in $EXISTING_IDS; do
  curl -s -X DELETE -H "Authorization: $TOKEN" \
    "$MEALIE_URL/api/households/mealplans/$ID" > /dev/null
done

# Step 2: Look up recipe UUID from slug.
UUID=$(curl -s -H "Authorization: $TOKEN" "$MEALIE_URL/api/recipes/$SLUG" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$UUID" ]; then
  echo "Failed to look up UUID for slug: $SLUG" >&2
  exit 1
fi

# Step 3: Create the new mealplan entry.
curl -s -X POST -H "Authorization: $TOKEN" -H "Content-Type: application/json" \
  -d "{\"date\": \"$DATE\", \"entry_type\": \"$ENTRY_TYPE\", \"recipe_id\": \"$UUID\"}" \
  "$MEALIE_URL/api/households/mealplans" > /dev/null

echo "OK: $SLUG ($UUID) → $DATE (replaced $(echo $EXISTING_IDS | wc -w | tr -d ' ') old entries)"
