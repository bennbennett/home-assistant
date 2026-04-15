#!/usr/bin/env python3
"""
Monitor Home Assistant lights for changes
Helps identify what's causing mysterious dimming
"""

import os
import json
import time
import requests
from datetime import datetime

# Load configuration from environment variables
# Run: source ../.env && export HASS_URL HASS_TOKEN && python3 monitor_lights.py
HASS_URL = os.environ.get('HASS_URL')
HASS_TOKEN = os.environ.get('HASS_TOKEN')

if not HASS_URL or not HASS_TOKEN:
    print("Error: HASS_URL and HASS_TOKEN environment variables required.")
    print("Run: source ../.env && export HASS_URL HASS_TOKEN")
    exit(1)

headers = {
    "Authorization": f"Bearer {HASS_TOKEN}",
    "Content-Type": "application/json"
}

def get_light_states():
    """Get current state of all lights"""
    response = requests.get(f"{HASS_URL}/api/states", headers=headers)
    if response.status_code == 200:
        states = response.json()
        lights = {}
        for state in states:
            if state['entity_id'].startswith('light.'):
                lights[state['entity_id']] = {
                    'state': state['state'],
                    'brightness': state.get('attributes', {}).get('brightness'),
                    'last_changed': state.get('last_changed')
                }
        return lights
    return {}

def monitor_changes(duration_minutes=5):
    """Monitor for changes over specified duration"""
    print(f"Starting light monitoring at {datetime.now().strftime('%I:%M:%S %p')}")
    print(f"Monitoring for {duration_minutes} minutes...")
    print("-" * 50)

    previous_states = get_light_states()
    end_time = time.time() + (duration_minutes * 60)

    while time.time() < end_time:
        time.sleep(10)  # Check every 10 seconds
        current_states = get_light_states()

        # Check for changes
        for entity_id, current in current_states.items():
            if entity_id in previous_states:
                prev = previous_states[entity_id]

                # Check if state or brightness changed
                if (prev['state'] != current['state'] or
                    prev['brightness'] != current['brightness']):

                    timestamp = datetime.now().strftime('%I:%M:%S %p')
                    print(f"\n🔔 CHANGE DETECTED at {timestamp}")
                    print(f"   Entity: {entity_id}")
                    print(f"   State: {prev['state']} → {current['state']}")

                    if prev['brightness'] != current['brightness']:
                        prev_bright = f"{int(prev['brightness']/255*100)}%" if prev['brightness'] else "N/A"
                        curr_bright = f"{int(current['brightness']/255*100)}%" if current['brightness'] else "N/A"
                        print(f"   Brightness: {prev_bright} → {curr_bright}")

                    # Try to identify what caused the change
                    check_recent_triggers(entity_id)
                    print("-" * 50)

        previous_states = current_states

    print(f"\nMonitoring completed at {datetime.now().strftime('%I:%M:%S %p')}")

def check_recent_triggers(entity_id):
    """Check what might have triggered the change"""
    # Check logbook for recent entries
    try:
        response = requests.get(
            f"{HASS_URL}/api/logbook?entity={entity_id}&num_days=0",
            headers=headers
        )
        if response.status_code == 200:
            entries = response.json()
            if entries and len(entries) > 0:
                latest = entries[-1]
                print(f"   Trigger: {latest.get('message', 'Unknown')}")
                if 'context_user_id' in latest:
                    print(f"   User: {latest.get('context_user_id', 'Unknown')}")
    except:
        pass

if __name__ == "__main__":
    print("Home Assistant Light Monitor")
    print("=" * 50)

    # Run for 5 minutes around expected trigger times
    monitor_changes(5)