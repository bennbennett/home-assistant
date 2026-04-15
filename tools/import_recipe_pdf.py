#!/usr/bin/env python3
"""Import recipe PDFs into Mealie.

Two extraction paths:
  1. Claude Code path: Claude reads PDF, extracts JSON, passes via --json flag.
     Only requires `requests` (no pdfplumber or anthropic needed).
  2. Standalone path: Uses pdfplumber + Anthropic API (Haiku) for extraction.
     For batch/unattended use.

Usage:
  # Claude Code path (pre-extracted JSON)
  . .env && python3 tools/import_recipe_pdf.py --json '{"name": "...", ...}'
  . .env && python3 tools/import_recipe_pdf.py --json -   # from stdin

  # Standalone (AI extraction from PDF)
  . .env && python3 tools/import_recipe_pdf.py recipe.pdf
  . .env && python3 tools/import_recipe_pdf.py *.pdf
  . .env && python3 tools/import_recipe_pdf.py --folder ~/Recipes/

  # Options
  --preview     Show extracted recipe, don't push to Mealie
  --dry-run     Show JSON that would be sent to Mealie API

Environment variables (from .env):
  MEALIE_URL       Mealie server URL (e.g., http://100.68.225.20:9925)
  MEALIE_TOKEN     Mealie API token
  ANTHROPIC_API_KEY  Anthropic API key (only needed for standalone PDF mode)
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

RECIPE_SCHEMA_PROMPT = """\
Extract the recipe from this text and return valid JSON matching this exact schema.
If there are multiple sub-recipes (e.g., a main dish with sides), merge them into ONE recipe.
Combine all ingredients into a single list (group by sub-recipe with a header like "--- For the Sauce ---").
Combine all instructions into a single numbered sequence.

JSON schema:
{
  "name": "Recipe Name",
  "description": "Brief 1-2 sentence description of the dish",
  "recipeYield": "4 servings",
  "prepTime": "15 Minutes",
  "cookTime": "30 Minutes",
  "totalTime": "45 Minutes",
  "recipeIngredient": [
    {"note": "1 lb shrimp, peeled and deveined"},
    {"note": "2 tbsp olive oil"}
  ],
  "recipeInstructions": [
    {"text": "Step 1 text here."},
    {"text": "Step 2 text here."}
  ],
  "tags": [{"name": "dinner"}, {"name": "seafood"}],
  "recipeCategory": [{"name": "Main Dish"}]
}

Rules:
- Return ONLY the JSON object, no markdown fences or extra text
- Use the exact field names shown above
- For ingredients, put the full text (amount + unit + item + notes) in the "note" field
- For times, use the format "X Minutes" or "X Hours Y Minutes"
- If a time is not specified, omit that field entirely
- For tags, infer 2-4 relevant tags (e.g., cuisine type, meal type, protein, cooking method)
- For recipeCategory, pick ONE from: Main Dish, Side Dish, Appetizer, Dessert, Soup, Salad, Breakfast, Snack, Beverage, Sauce, Bread
- If the recipe has sub-recipes, use "--- Sub-recipe Name ---" as a note entry before that group's ingredients
- Keep instruction steps concise but complete
"""


def check_mealie_connection(base_url: str, token: str) -> bool:
    """Verify Mealie is reachable."""
    try:
        resp = requests.get(
            f"{base_url}/api/app/about",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        return resp.status_code == 200
    except requests.ConnectionError:
        return False


def to_jsonld(recipe_data: dict) -> dict:
    """Convert internal recipe format to schema.org JSON-LD for Mealie import."""
    ld = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": recipe_data.get("name", "Untitled Recipe"),
    }

    if v := recipe_data.get("description"):
        ld["description"] = v
    if v := recipe_data.get("recipeYield"):
        ld["recipeYield"] = v

    # Convert human-readable times to ISO 8601 duration
    for field in ("prepTime", "cookTime", "totalTime"):
        if v := recipe_data.get(field):
            ld[field] = to_iso_duration(v)

    # Ingredients: flatten from [{note: "..."}] to ["..."]
    if ingredients := recipe_data.get("recipeIngredient"):
        ld["recipeIngredient"] = [
            ing.get("note", "") if isinstance(ing, dict) else str(ing)
            for ing in ingredients
        ]

    # Instructions: flatten from [{text: "..."}] to [{@type, text}]
    if instructions := recipe_data.get("recipeInstructions"):
        ld["recipeInstructions"] = [
            {"@type": "HowToStep", "text": step.get("text", "") if isinstance(step, dict) else str(step)}
            for step in instructions
        ]

    # Tags as comma-separated keywords
    if tags := recipe_data.get("tags"):
        ld["keywords"] = ", ".join(
            t.get("name", "") if isinstance(t, dict) else str(t)
            for t in tags
        )

    # Category as flat list
    if cats := recipe_data.get("recipeCategory"):
        ld["recipeCategory"] = [
            c.get("name", "") if isinstance(c, dict) else str(c)
            for c in cats
        ]

    return ld


def to_iso_duration(time_str: str) -> str:
    """Convert human-readable time to ISO 8601 duration (e.g., '1 Hour 30 Minutes' -> 'PT1H30M')."""
    time_lower = time_str.lower().strip()
    hours = 0
    minutes = 0

    import re
    h_match = re.search(r"(\d+)\s*hour", time_lower)
    m_match = re.search(r"(\d+)\s*min", time_lower)

    if h_match:
        hours = int(h_match.group(1))
    if m_match:
        minutes = int(m_match.group(1))

    if hours == 0 and minutes == 0:
        # Fallback: return original string (Mealie may parse it)
        return time_str

    parts = "PT"
    if hours:
        parts += f"{hours}H"
    if minutes:
        parts += f"{minutes}M"
    return parts


def create_recipe_in_mealie(
    base_url: str, token: str, recipe_data: dict, dry_run: bool = False
) -> dict | None:
    """Create a recipe in Mealie via the JSON-LD import endpoint.

    Uses /api/recipes/create/html-or-json with schema.org JSON-LD format,
    which reliably imports ingredients, instructions, tags, and all metadata.

    Returns the created recipe dict or None on failure.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    name = recipe_data.get("name", "Untitled Recipe")
    jsonld = to_jsonld(recipe_data)

    if dry_run:
        print(f"\n[DRY RUN] Would create recipe: {name}")
        print(f"[DRY RUN] POST {base_url}/api/recipes/create/html-or-json")
        print(f"[DRY RUN] JSON-LD payload:")
        print(json.dumps(jsonld, indent=2))
        return {"slug": name.lower().replace(" ", "-"), "dry_run": True}

    print(f"  Importing recipe: {name}...")
    resp = requests.post(
        f"{base_url}/api/recipes/create/html-or-json",
        headers=headers,
        json={"data": json.dumps(jsonld), "includeTags": True},
        timeout=15,
    )

    if resp.status_code not in (200, 201):
        print(f"  ERROR: Failed to create recipe (HTTP {resp.status_code})")
        print(f"  Response: {resp.text[:500]}")
        return None

    slug = resp.json() if isinstance(resp.json(), str) else resp.json().get("slug", "")
    if not slug:
        print("  ERROR: No slug returned from import")
        return None

    # Fetch the created recipe to return full data
    resp2 = requests.get(
        f"{base_url}/api/recipes/{slug}",
        headers=headers,
        timeout=10,
    )

    recipe_url = f"{base_url}/g/home/r/{slug}"
    print(f"  Success! Recipe URL: {recipe_url}")

    if resp2.status_code == 200:
        return resp2.json()
    return {"slug": slug}


def preview_recipe(recipe_data: dict) -> None:
    """Pretty-print a recipe for review."""
    print(f"\n{'=' * 60}")
    print(f"  {recipe_data.get('name', 'Untitled')}")
    print(f"{'=' * 60}")

    if desc := recipe_data.get("description"):
        print(f"\n  {desc}")

    times = []
    if t := recipe_data.get("prepTime"):
        times.append(f"Prep: {t}")
    if t := recipe_data.get("cookTime"):
        times.append(f"Cook: {t}")
    if t := recipe_data.get("totalTime"):
        times.append(f"Total: {t}")
    if times:
        print(f"\n  {' | '.join(times)}")

    if y := recipe_data.get("recipeYield"):
        print(f"  Yield: {y}")

    if cats := recipe_data.get("recipeCategory"):
        print(f"  Category: {', '.join(c['name'] for c in cats)}")

    if tags := recipe_data.get("tags"):
        print(f"  Tags: {', '.join(t['name'] for t in tags)}")

    if ingredients := recipe_data.get("recipeIngredient"):
        print(f"\n  INGREDIENTS ({len(ingredients)}):")
        for ing in ingredients:
            note = ing.get("note", "")
            if note.startswith("---"):
                print(f"\n  {note}")
            else:
                print(f"    - {note}")

    if instructions := recipe_data.get("recipeInstructions"):
        print(f"\n  INSTRUCTIONS ({len(instructions)} steps):")
        for i, step in enumerate(instructions, 1):
            text = step.get("text", "")
            # Wrap long lines
            if len(text) > 70:
                words = text.split()
                lines = []
                line = ""
                for word in words:
                    if len(line) + len(word) + 1 > 70:
                        lines.append(line)
                        line = word
                    else:
                        line = f"{line} {word}" if line else word
                if line:
                    lines.append(line)
                print(f"    {i}. {lines[0]}")
                for ln in lines[1:]:
                    print(f"       {ln}")
            else:
                print(f"    {i}. {text}")

    print(f"\n{'=' * 60}")


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF using pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        print("ERROR: pdfplumber is required for PDF extraction.")
        print("Install it: pip3 install pdfplumber")
        sys.exit(1)

    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

    return "\n\n".join(text_parts)


def extract_recipe_with_ai(text: str) -> dict:
    """Use Anthropic API (Haiku) to extract structured recipe data from text."""
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic is required for AI extraction.")
        print("Install it: pip3 install anthropic")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        print("Add it to your .env file or export it.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": f"{RECIPE_SCHEMA_PROMPT}\n\nHere is the recipe text:\n\n{text}",
            }
        ],
    )

    response_text = message.content[0].text.strip()

    # Strip markdown fences if present
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        # Remove first line (```json or ```) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        response_text = "\n".join(lines)

    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse AI response as JSON: {e}")
        print(f"Response was:\n{response_text[:1000]}")
        sys.exit(1)


def process_pdf(
    pdf_path: str,
    base_url: str,
    token: str,
    preview: bool = False,
    dry_run: bool = False,
) -> dict | None:
    """Process a single PDF file: extract text, structure with AI, push to Mealie."""
    path = Path(pdf_path)
    if not path.exists():
        print(f"ERROR: File not found: {pdf_path}")
        return None

    print(f"\nProcessing: {path.name}")
    print(f"  Extracting text from PDF...")
    text = extract_text_from_pdf(str(path))

    if not text.strip():
        print(f"  ERROR: No text extracted from {path.name}")
        return None

    print(f"  Extracted {len(text)} chars from {path.name}")
    print(f"  Structuring recipe with AI...")

    recipe_data = extract_recipe_with_ai(text)

    if preview or dry_run:
        preview_recipe(recipe_data)
        if dry_run:
            create_recipe_in_mealie(base_url, token, recipe_data, dry_run=True)
        return recipe_data

    preview_recipe(recipe_data)
    return create_recipe_in_mealie(base_url, token, recipe_data)


def process_json_input(
    json_input: str,
    base_url: str,
    token: str,
    preview: bool = False,
    dry_run: bool = False,
) -> dict | None:
    """Process pre-extracted JSON recipe data."""
    if json_input == "-":
        json_input = sys.stdin.read()

    try:
        recipe_data = json.loads(json_input)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON input: {e}")
        sys.exit(1)

    if not recipe_data.get("name"):
        print("ERROR: Recipe JSON must include a 'name' field.")
        sys.exit(1)

    if preview:
        preview_recipe(recipe_data)
        return recipe_data

    if dry_run:
        preview_recipe(recipe_data)
        create_recipe_in_mealie(base_url, token, recipe_data, dry_run=True)
        return recipe_data

    preview_recipe(recipe_data)
    return create_recipe_in_mealie(base_url, token, recipe_data)


def main():
    parser = argparse.ArgumentParser(
        description="Import recipe PDFs into Mealie",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # From pre-extracted JSON (Claude Code path)
  python3 import_recipe_pdf.py --json '{"name": "Pasta", ...}'
  echo '{"name": "Pasta", ...}' | python3 import_recipe_pdf.py --json -

  # From PDF files (standalone path, requires pdfplumber + anthropic)
  python3 import_recipe_pdf.py recipe.pdf
  python3 import_recipe_pdf.py *.pdf
  python3 import_recipe_pdf.py --folder ~/Recipes/

  # Preview / dry run
  python3 import_recipe_pdf.py --preview recipe.pdf
  python3 import_recipe_pdf.py --dry-run --json '{"name": "Pasta", ...}'
""",
    )

    parser.add_argument(
        "files", nargs="*", help="PDF files to import"
    )
    parser.add_argument(
        "--json",
        dest="json_input",
        metavar="JSON",
        help="Import from pre-extracted JSON (use '-' for stdin)",
    )
    parser.add_argument(
        "--folder",
        metavar="DIR",
        help="Import all PDFs from a directory",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Show extracted recipe without pushing to Mealie",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be sent to Mealie API",
    )

    args = parser.parse_args()

    # Validate environment
    base_url = os.environ.get("MEALIE_URL")
    token = os.environ.get("MEALIE_TOKEN")

    if not base_url or not token:
        print("ERROR: MEALIE_URL and MEALIE_TOKEN must be set.")
        print("Run: . .env")
        sys.exit(1)

    # Strip trailing slash
    base_url = base_url.rstrip("/")

    # Check Mealie connectivity (skip for preview-only)
    if not args.preview:
        print(f"Connecting to Mealie at {base_url}...")
        if not check_mealie_connection(base_url, token):
            print("ERROR: Cannot connect to Mealie. Check URL and token.")
            sys.exit(1)
        print("Connected.")

    # Route to appropriate handler
    if args.json_input is not None:
        result = process_json_input(
            args.json_input, base_url, token, args.preview, args.dry_run
        )
        if result and not args.preview and not args.dry_run:
            slug = result.get("slug", "")
            if slug:
                print(f"\nRecipe URL: {base_url}/g/home/r/{slug}")
        sys.exit(0)

    # Collect PDF files
    pdf_files = []
    if args.folder:
        folder = Path(args.folder)
        if not folder.is_dir():
            print(f"ERROR: Directory not found: {args.folder}")
            sys.exit(1)
        pdf_files = sorted(folder.glob("*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in {args.folder}")
            sys.exit(1)

    if args.files:
        pdf_files.extend(Path(f) for f in args.files)

    if not pdf_files:
        parser.print_help()
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDF file(s) to process")

    success = 0
    failed = 0
    for pdf_path in pdf_files:
        result = process_pdf(
            str(pdf_path), base_url, token, args.preview, args.dry_run
        )
        if result:
            success += 1
        else:
            failed += 1

    print(f"\nDone: {success} imported, {failed} failed out of {len(pdf_files)} total")


if __name__ == "__main__":
    main()
