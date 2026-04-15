#!/usr/bin/env python3
"""Generate a weekly grocery list from the Mealie meal plan.

Reads the current week's meal plan from Home Assistant, then uses Mealie's
native recipe-to-shopping-list endpoint to populate a "Weekly Groceries"
shopping list with all required ingredients.

Usage:
  . .env && python3 tools/generate_grocery_list.py              # Generate list
  . .env && python3 tools/generate_grocery_list.py --preview     # Preview only
  . .env && python3 tools/generate_grocery_list.py --sync        # Generate + Google Keep sync
  . .env && python3 tools/generate_grocery_list.py --clear       # Clear the shopping list

Environment variables (from .env):
  MEALIE_URL       Mealie server URL
  MEALIE_TOKEN     Mealie API token
  HASS_URL         Home Assistant URL
  HASS_TOKEN       Home Assistant long-lived access token
"""

import argparse
import os
import sys

import requests

SHOPPING_LIST_NAME = "Weekly Groceries"


def mealie_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def ha_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def check_mealie(base_url: str, token: str) -> bool:
    """Verify Mealie is reachable."""
    try:
        resp = requests.get(
            f"{base_url}/api/app/about",
            headers=mealie_headers(token),
            timeout=5,
        )
        return resp.status_code == 200
    except requests.ConnectionError:
        return False


def check_ha(hass_url: str, token: str) -> bool:
    """Verify Home Assistant is reachable."""
    try:
        resp = requests.get(
            f"{hass_url}/api/",
            headers=ha_headers(token),
            timeout=5,
        )
        return resp.status_code == 200
    except requests.ConnectionError:
        return False


def get_mealplan_recipes(hass_url: str, hass_token: str) -> list[dict]:
    """Fetch unique recipes from the weekly meal plan sensor.

    Returns list of dicts with 'recipe_name' and 'recipe_slug' keys.
    """
    resp = requests.get(
        f"{hass_url}/api/states/sensor.mealie_weekly_meal_plan",
        headers=ha_headers(hass_token),
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"ERROR: Could not fetch meal plan sensor (HTTP {resp.status_code})")
        sys.exit(1)

    data = resp.json()
    meals = data.get("attributes", {}).get("meals", [])

    if not meals:
        print("No meals found in the weekly meal plan.")
        return []

    # Deduplicate by slug, preserving order
    seen = set()
    unique = []
    for meal in meals:
        name = meal.get("recipe_name", "")
        slug = meal.get("recipe_slug", "")
        # Skip empty / cleared meals
        if not name or not slug:
            continue
        if slug not in seen:
            seen.add(slug)
            unique.append({"recipe_name": name, "recipe_slug": slug})

    return unique


def find_or_create_shopping_list(base_url: str, token: str) -> str:
    """Find the 'Weekly Groceries' shopping list, or create it. Returns list ID."""
    headers = mealie_headers(token)

    # List all shopping lists
    resp = requests.get(
        f"{base_url}/api/households/shopping/lists",
        headers=headers,
        params={"perPage": 100},
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"ERROR: Could not list shopping lists (HTTP {resp.status_code})")
        sys.exit(1)

    data = resp.json()
    items = data.get("items", [])

    for lst in items:
        if lst.get("name") == SHOPPING_LIST_NAME:
            print(f"  Found existing list: {SHOPPING_LIST_NAME} (id: {lst['id']})")
            return lst["id"]

    # Create new list
    resp = requests.post(
        f"{base_url}/api/households/shopping/lists",
        headers=headers,
        json={"name": SHOPPING_LIST_NAME},
        timeout=10,
    )
    if resp.status_code not in (200, 201):
        print(f"ERROR: Could not create shopping list (HTTP {resp.status_code})")
        print(f"  Response: {resp.text[:500]}")
        sys.exit(1)

    list_id = resp.json().get("id")
    print(f"  Created new list: {SHOPPING_LIST_NAME} (id: {list_id})")
    return list_id


def clear_shopping_list(base_url: str, token: str, list_id: str) -> int:
    """Remove all items from a shopping list. Returns count of items removed."""
    headers = mealie_headers(token)

    resp = requests.get(
        f"{base_url}/api/households/shopping/lists/{list_id}",
        headers=headers,
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"ERROR: Could not fetch list details (HTTP {resp.status_code})")
        return 0

    list_items = resp.json().get("listItems", [])
    if not list_items:
        return 0

    count = 0
    for item in list_items:
        del_resp = requests.delete(
            f"{base_url}/api/households/shopping/items/{item['id']}",
            headers=headers,
            timeout=10,
        )
        if del_resp.status_code in (200, 204):
            count += 1

    return count


def get_recipe_id(base_url: str, token: str, slug: str) -> str | None:
    """Get a recipe's ID from its slug."""
    resp = requests.get(
        f"{base_url}/api/recipes/{slug}",
        headers=mealie_headers(token),
        timeout=10,
    )
    if resp.status_code != 200:
        return None
    return resp.json().get("id")


def add_recipe_to_list(base_url: str, token: str, list_id: str, recipe_id: str) -> bool:
    """Add a recipe's ingredients to a shopping list via Mealie's native endpoint."""
    resp = requests.post(
        f"{base_url}/api/households/shopping/lists/{list_id}/recipe/{recipe_id}",
        headers=mealie_headers(token),
        timeout=15,
    )
    return resp.status_code in (200, 201)


def clean_section_headers(base_url: str, token: str, list_id: str) -> int:
    """Remove items that are section headers (note starts with '---')."""
    headers = mealie_headers(token)

    resp = requests.get(
        f"{base_url}/api/households/shopping/lists/{list_id}",
        headers=headers,
        timeout=10,
    )
    if resp.status_code != 200:
        return 0

    list_items = resp.json().get("listItems", [])
    removed = 0
    for item in list_items:
        note = item.get("note", "") or item.get("display", "") or ""
        if note.strip().startswith("---"):
            del_resp = requests.delete(
                f"{base_url}/api/households/shopping/items/{item['id']}",
                headers=headers,
                timeout=10,
            )
            if del_resp.status_code in (200, 204):
                removed += 1

    return removed


def get_final_list(base_url: str, token: str, list_id: str) -> list[dict]:
    """Fetch the final shopping list items."""
    resp = requests.get(
        f"{base_url}/api/households/shopping/lists/{list_id}",
        headers=mealie_headers(token),
        timeout=10,
    )
    if resp.status_code != 200:
        return []
    return resp.json().get("listItems", [])


def trigger_keep_sync(hass_url: str, hass_token: str) -> bool:
    """Press the sync shopping list button to trigger Google Keep sync."""
    resp = requests.post(
        f"{hass_url}/api/services/input_button/press",
        headers=ha_headers(hass_token),
        json={"entity_id": "input_button.sync_shopping_list"},
        timeout=10,
    )
    return resp.status_code == 200


def preview_recipes(recipes: list[dict], base_url: str, token: str):
    """Show what recipes would be added and their ingredient counts."""
    print(f"\n{'=' * 60}")
    print(f"  Weekly Meal Plan — {len(recipes)} unique recipe(s)")
    print(f"{'=' * 60}")

    for recipe in recipes:
        slug = recipe["recipe_slug"]
        name = recipe["recipe_name"]

        resp = requests.get(
            f"{base_url}/api/recipes/{slug}",
            headers=mealie_headers(token),
            timeout=10,
        )
        if resp.status_code != 200:
            print(f"\n  {name}")
            print(f"    (could not fetch recipe details)")
            continue

        data = resp.json()
        ingredients = data.get("recipeIngredient", [])
        print(f"\n  {name} ({len(ingredients)} ingredients)")
        for ing in ingredients:
            note = ing.get("display", "") or ing.get("note", "") or ""
            if note.strip().startswith("---"):
                print(f"    {note.strip()}")
            else:
                print(f"    - {note}")

    print(f"\n{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a weekly grocery list from the Mealie meal plan",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  . .env && python3 tools/generate_grocery_list.py              # Generate list
  . .env && python3 tools/generate_grocery_list.py --preview     # Preview only
  . .env && python3 tools/generate_grocery_list.py --sync        # Generate + Keep sync
  . .env && python3 tools/generate_grocery_list.py --clear       # Clear list only
""",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Show recipes and ingredients without modifying the shopping list",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="After generating, trigger Google Keep sync via HA",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Just clear the shopping list (don't add new items)",
    )

    args = parser.parse_args()

    # Validate environment
    mealie_url = os.environ.get("MEALIE_URL", "").rstrip("/")
    mealie_token = os.environ.get("MEALIE_TOKEN", "")
    hass_url = os.environ.get("HASS_URL", "").rstrip("/")
    hass_token = os.environ.get("HASS_TOKEN", "")

    if not mealie_url or not mealie_token:
        print("ERROR: MEALIE_URL and MEALIE_TOKEN must be set.")
        print("Run: . .env")
        sys.exit(1)

    if not hass_url or not hass_token:
        print("ERROR: HASS_URL and HASS_TOKEN must be set.")
        print("Run: . .env")
        sys.exit(1)

    # Connectivity checks
    print("Checking connectivity...")
    if not check_mealie(mealie_url, mealie_token):
        print("ERROR: Cannot connect to Mealie. Check MEALIE_URL and MEALIE_TOKEN.")
        sys.exit(1)
    print(f"  Mealie: OK ({mealie_url})")

    if not check_ha(hass_url, hass_token):
        print("ERROR: Cannot connect to Home Assistant. Check HASS_URL and HASS_TOKEN.")
        sys.exit(1)
    print(f"  Home Assistant: OK ({hass_url})")

    # Clear-only mode
    if args.clear:
        list_id = find_or_create_shopping_list(mealie_url, mealie_token)
        removed = clear_shopping_list(mealie_url, mealie_token, list_id)
        print(f"\nCleared {removed} item(s) from {SHOPPING_LIST_NAME}.")
        return

    # Fetch recipes from mealplan
    print("\nFetching weekly meal plan from Home Assistant...")
    recipes = get_mealplan_recipes(hass_url, hass_token)

    if not recipes:
        print("No recipes assigned this week. Nothing to do.")
        return

    print(f"  Found {len(recipes)} unique recipe(s):")
    for r in recipes:
        print(f"    - {r['recipe_name']}")

    # Preview mode
    if args.preview:
        preview_recipes(recipes, mealie_url, mealie_token)
        return

    # Generate the grocery list
    print(f"\nPreparing shopping list: {SHOPPING_LIST_NAME}")
    list_id = find_or_create_shopping_list(mealie_url, mealie_token)

    # Clear existing items
    removed = clear_shopping_list(mealie_url, mealie_token, list_id)
    if removed:
        print(f"  Cleared {removed} existing item(s)")

    # Add each recipe's ingredients
    print("\nAdding recipe ingredients...")
    for recipe in recipes:
        slug = recipe["recipe_slug"]
        name = recipe["recipe_name"]
        recipe_id = get_recipe_id(mealie_url, mealie_token, slug)
        if not recipe_id:
            print(f"  SKIP: Could not find recipe ID for '{name}' (slug: {slug})")
            continue

        if add_recipe_to_list(mealie_url, mealie_token, list_id, recipe_id):
            print(f"  Added: {name}")
        else:
            print(f"  FAIL: Could not add '{name}' to list")

    # Clean up section headers
    cleaned = clean_section_headers(mealie_url, mealie_token, list_id)
    if cleaned:
        print(f"  Removed {cleaned} section header(s)")

    # Fetch and display final list
    final_items = get_final_list(mealie_url, mealie_token, list_id)
    unchecked = [i for i in final_items if not i.get("checked", False)]

    print(f"\n{'=' * 60}")
    print(f"  {SHOPPING_LIST_NAME} — {len(unchecked)} item(s)")
    print(f"{'=' * 60}")
    for item in unchecked:
        display = item.get("display", "") or item.get("note", "") or "(unnamed)"
        print(f"  [ ] {display}")
    print(f"{'=' * 60}")

    list_url = f"{mealie_url}/shopping-lists/{list_id}"
    print(f"\nMealie shopping list: {list_url}")

    # Google Keep sync
    if args.sync:
        print("\nTriggering Google Keep sync...")
        if trigger_keep_sync(hass_url, hass_token):
            print("  Sync triggered. Items will appear in Google Keep shortly.")
        else:
            print("  WARNING: Could not trigger Keep sync. Try pressing the button manually in HA.")

    print("\nDone!")


if __name__ == "__main__":
    main()
