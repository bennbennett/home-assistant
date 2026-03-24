# Home Assistant Tools

Helper scripts for interacting with Home Assistant.

## Prerequisites

Before using any tool, load credentials:
```bash
cd /Users/bbennett/Documents/25_PERSONAL-Environment/home-assistant
source .env && export HASS_URL HASS_TOKEN
```

## hass-setup.sh

Bash helper script with common API functions.

### Usage

```bash
./hass-setup.sh <command> [arguments]
```

### Commands

| Command | Arguments | Description |
|---------|-----------|-------------|
| `test` | - | Test connection to Home Assistant |
| `summary` | - | Show entity count by domain |
| `states` | [filter] | Get entity states (optional domain filter) |
| `entity` | entity_id | Get detailed state of specific entity |
| `service` | domain service [data] | Call a service |

### Examples

```bash
# Test connection
./hass-setup.sh test

# Get summary
./hass-setup.sh summary

# Get all light states
./hass-setup.sh states light

# Get specific entity
./hass-setup.sh entity light.living_room

# Call service
./hass-setup.sh service light turn_on '{"entity_id":"light.living_room"}'
./hass-setup.sh service light turn_on '{"entity_id":"light.living_room","brightness_pct":50}'
```

## monitor_lights.py

Python script to monitor light changes in real-time. Useful for debugging unexpected dimming or state changes.

### Usage

```bash
# Load credentials first
source ../.env && export HASS_URL HASS_TOKEN

# Run monitor (default 5 minutes)
python3 monitor_lights.py
```

### What it Does

- Polls all light entities every 10 seconds
- Reports any state or brightness changes
- Shows timestamps and change details
- Attempts to identify what triggered changes via logbook

### Requirements

- Python 3
- `requests` library (`pip3 install requests`)

### Example Output

```
Home Assistant Light Monitor
==================================================
Starting light monitoring at 09:30:15 PM
Monitoring for 5 minutes...
--------------------------------------------------

🔔 CHANGE DETECTED at 09:31:25 PM
   Entity: light.living_room
   State: on → on
   Brightness: 100% → 50%
   Trigger: called service light.turn_on
--------------------------------------------------

Monitoring completed at 09:35:15 PM
```

## import_recipe_pdf.py

Import recipe PDFs into Mealie. Supports two extraction paths:

1. **Claude Code path** — Claude reads the PDF, extracts structured JSON, passes via `--json`. Only requires `requests`.
2. **Standalone path** — Uses `pdfplumber` + Anthropic API (Haiku) for text extraction and structuring. For batch/unattended use.

### Requirements

```bash
# Claude Code path (--json mode)
pip3 install requests

# Standalone PDF mode
pip3 install pdfplumber anthropic requests
```

### Environment Variables

- `MEALIE_URL` — Mealie server URL (already in `.env`)
- `MEALIE_TOKEN` — Mealie API token (already in `.env`)
- `ANTHROPIC_API_KEY` — Anthropic API key (only needed for standalone PDF mode)

### Usage

```bash
# Load credentials
. .env

# Claude Code path: pre-extracted JSON
python3 tools/import_recipe_pdf.py --json '{"name": "Pasta Carbonara", "recipeIngredient": [{"note": "1 lb spaghetti"}], ...}'
echo '{"name": "Pasta"}' | python3 tools/import_recipe_pdf.py --json -

# Standalone: single PDF
python3 tools/import_recipe_pdf.py recipe.pdf

# Standalone: multiple PDFs
python3 tools/import_recipe_pdf.py *.pdf

# Standalone: all PDFs in a folder
python3 tools/import_recipe_pdf.py --folder ~/Recipes/

# Preview extracted recipe (don't push to Mealie)
python3 tools/import_recipe_pdf.py --preview recipe.pdf

# Dry run (show API calls without executing)
python3 tools/import_recipe_pdf.py --dry-run recipe.pdf
```

### Recipe JSON Schema

When using `--json` mode, provide JSON in this format:

```json
{
  "name": "Recipe Name",
  "description": "Brief description",
  "recipeYield": "4 servings",
  "prepTime": "15 Minutes",
  "cookTime": "30 Minutes",
  "totalTime": "45 Minutes",
  "recipeIngredient": [
    {"note": "1 lb shrimp, peeled and deveined"},
    {"note": "2 tbsp olive oil"}
  ],
  "recipeInstructions": [
    {"text": "Step 1 text."},
    {"text": "Step 2 text."}
  ],
  "tags": [{"name": "dinner"}, {"name": "seafood"}],
  "recipeCategory": [{"name": "Main Dish"}]
}
```

### Claude Code Workflow

When asked to import a recipe PDF:
1. Read the PDF with the Read tool
2. Extract structured JSON matching the schema above
3. Run: `. .env && python3 tools/import_recipe_pdf.py --json '<json>'`
4. Report the Mealie URL for the new recipe

## generate_grocery_list.py

Generate a combined grocery/shopping list from the week's Mealie meal plan. Uses Mealie's native recipe-to-shopping-list endpoint for ingredient grouping and deduplication.

### Requirements

```bash
pip3 install requests
```

### Environment Variables

- `MEALIE_URL` — Mealie server URL (already in `.env`)
- `MEALIE_TOKEN` — Mealie API token (already in `.env`)
- `HASS_URL` — Home Assistant URL (already in `.env`)
- `HASS_TOKEN` — Home Assistant token (already in `.env`)

### Usage

```bash
# Load credentials
. .env

# Generate grocery list from this week's meal plan
python3 tools/generate_grocery_list.py

# Preview recipes + ingredients without modifying
python3 tools/generate_grocery_list.py --preview

# Generate and sync to Google Keep
python3 tools/generate_grocery_list.py --sync

# Clear the shopping list
python3 tools/generate_grocery_list.py --clear
```

### How It Works

1. Reads `sensor.mealie_weekly_meal_plan` from HA to get the week's recipes
2. Finds or creates a "Weekly Groceries" shopping list in Mealie
3. Clears existing items, then adds each recipe's ingredients via Mealie's native endpoint
4. Removes section headers (lines starting with `---`)
5. Optionally triggers Google Keep sync via `input_button.sync_shopping_list`

### Dashboard Integration

A "Grocery List" button appears in the Weekly Dinners section of the Home Hub Meals view. Tapping it opens a popup with the `todo-list` card for `todo.mealie_weekly_groceries`, with buttons to clear all items or send to Google Keep. `Clear All` is handled by `script.clear_weekly_groceries`, which removes all grocery items from the list, not just completed ones.

## Adding New Tools

When adding new tools:

1. Place in this `tools/` directory
2. Use environment variables for credentials (never hardcode)
3. Add documentation to this README
4. Make scripts executable: `chmod +x script_name`
