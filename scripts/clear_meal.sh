#!/bin/bash
# clear_meal.sh — Delete the dinner mealplan entry for a given date.
# Called by HA shell_command.mealie_clear_meal with a date argument.
#
# Replaces the previous "__HA_CLEARED__ sentinel note" approach, which just
# appended another entry on top of whatever was there. This actually removes
# the entry so one-entry-per-date stays true.

set -u

DATE="$1"
ENTRY_TYPE="dinner"
MEALIE_URL="http://100.68.225.20:9925"
TOKEN=$(grep 'mealie_token_header' /config/secrets.yaml | sed 's/.*: *"*//' | sed 's/"*$//')

if [ -z "$DATE" ]; then
  echo "Usage: clear_meal.sh <date>" >&2
  exit 1
fi

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

COUNT=0
for ID in $EXISTING_IDS; do
  curl -s -X DELETE -H "Authorization: $TOKEN" \
    "$MEALIE_URL/api/households/mealplans/$ID" > /dev/null
  COUNT=$((COUNT + 1))
done

echo "OK: cleared $COUNT entries for $DATE"
