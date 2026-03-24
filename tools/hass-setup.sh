#!/bin/bash

# Home Assistant Helper Script for Claude Code
# This script sets up environment variables and provides helper functions

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Load environment variables
if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
    echo -e "${GREEN}✓ Home Assistant environment loaded${NC}"
    echo -e "${BLUE}  URL: $HASS_URL${NC}"
    echo -e "${BLUE}  Token: ${HASS_TOKEN:0:20}...${NC}"
else
    echo -e "${YELLOW}⚠ .env file not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Function to test connection
test_connection() {
    echo -e "${BLUE}Testing Home Assistant connection...${NC}"
    response=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/")
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ Connection successful!${NC}"
        return 0
    else
        echo -e "${YELLOW}✗ Connection failed (HTTP $response)${NC}"
        return 1
    fi
}

# Function to get all states (with optional filter)
get_states() {
    local filter=$1
    if [ -z "$filter" ]; then
        curl -s -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/states" | python3 -m json.tool
    else
        curl -s -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/states" | python3 -c "import sys, json; states=json.load(sys.stdin); filtered=[s for s in states if '$filter' in s['entity_id']]; print(json.dumps(filtered, indent=2))"
    fi
}

# Function to get a specific entity state
get_entity() {
    local entity_id=$1
    if [ -z "$entity_id" ]; then
        echo "Usage: get_entity <entity_id>"
        echo "Example: get_entity light.living_room"
        return 1
    fi
    curl -s -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/states/$entity_id" | python3 -m json.tool
}

# Function to call a service
call_service() {
    local domain=$1
    local service=$2
    local data=$3

    if [ -z "$domain" ] || [ -z "$service" ]; then
        echo "Usage: call_service <domain> <service> [json_data]"
        echo "Example: call_service light turn_on '{\"entity_id\": \"light.living_room\"}'"
        return 1
    fi

    if [ -z "$data" ]; then
        data="{}"
    fi

    curl -X POST -H "Authorization: Bearer $HASS_TOKEN" \
         -H "Content-Type: application/json" \
         -d "$data" \
         "$HASS_URL/api/services/$domain/$service" | python3 -m json.tool
}

# Function to get entity summary
entity_summary() {
    echo -e "${BLUE}Fetching entity summary...${NC}"
    curl -s -H "Authorization: Bearer $HASS_TOKEN" "$HASS_URL/api/states" | \
    python3 -c "
import sys, json
states = json.load(sys.stdin)
domains = {}
for s in states:
    domain = s['entity_id'].split('.')[0]
    domains[domain] = domains.get(domain, 0) + 1

print('\nEntity Summary by Domain:')
print('-' * 30)
for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
    print(f'{domain:20} {count:4} entities')
print('-' * 30)
total = len(states)
print(f'Total{\"\":16} {total:4} entities')
"
}

# Main execution
if [ "$1" = "test" ]; then
    test_connection
elif [ "$1" = "summary" ]; then
    entity_summary
elif [ "$1" = "states" ]; then
    get_states "$2"
elif [ "$1" = "entity" ]; then
    get_entity "$2"
elif [ "$1" = "service" ]; then
    call_service "$2" "$3" "$4"
else
    echo -e "${GREEN}Home Assistant Helper Script${NC}"
    echo "Environment variables have been set. You can now use:"
    echo ""
    echo "  \$HASS_URL    - Home Assistant URL"
    echo "  \$HASS_TOKEN  - Authentication token"
    echo ""
    echo "Helper functions available:"
    echo "  test_connection      - Test the connection"
    echo "  entity_summary       - Show entity count by domain"
    echo "  get_states [filter]  - Get all states (optionally filtered)"
    echo "  get_entity <id>      - Get specific entity state"
    echo "  call_service <domain> <service> [data] - Call a service"
    echo ""
    echo "Or run this script with:"
    echo "  $0 test                    - Test connection"
    echo "  $0 summary                  - Show entity summary"
    echo "  $0 states [filter]          - Get states"
    echo "  $0 entity <entity_id>       - Get entity"
    echo "  $0 service <domain> <service> [json] - Call service"
fi