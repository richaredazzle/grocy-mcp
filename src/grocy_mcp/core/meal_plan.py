"""Core meal plan management functions for Grocy."""

from __future__ import annotations

from grocy_mcp.client import GrocyClient
from grocy_mcp.core.resolve import resolve_recipe


async def meal_plan_list(client: GrocyClient) -> str:
    """Return a formatted list of meal plan entries."""
    entries = await client.get_objects("meal_plan")
    if not entries:
        return "No meal plan entries found."

    # Build recipe name map
    recipes = await client.get_objects("recipes")
    recipe_map = {r["id"]: r.get("name", f"Recipe {r['id']}") for r in recipes}

    # Sort by day
    entries.sort(key=lambda e: e.get("day", ""))

    lines = ["Meal plan:"]
    for entry in entries:
        day = entry.get("day", "?")
        recipe_id = entry.get("recipe_id")
        recipe_name = recipe_map.get(recipe_id, "")
        meal_type = entry.get("type", "")
        note = entry.get("note", "")

        parts = [f"  [{entry['id']}] {day}"]
        if meal_type:
            parts.append(f"({meal_type})")
        if recipe_name:
            parts.append(f"— {recipe_name}")
        if note:
            parts.append(f"— {note}")

        lines.append(" ".join(parts))

    return "\n".join(lines)


async def meal_plan_add(
    client: GrocyClient,
    day: str,
    recipe: str | None = None,
    note: str = "",
    meal_type: str = "",
) -> str:
    """Add an entry to the meal plan."""
    data: dict = {"day": day}

    if recipe is not None:
        recipe_id = await resolve_recipe(client, recipe)
        data["recipe_id"] = recipe_id
        data["type"] = meal_type or "recipe"
    else:
        data["type"] = meal_type or "note"

    if note:
        data["note"] = note

    entry_id = await client.create_object("meal_plan", data)
    label = f"recipe '{recipe}'" if recipe else f"note '{note}'"
    return f"Meal plan entry added for {day}: {label} (ID {entry_id})."


async def meal_plan_remove(client: GrocyClient, entry_id: int) -> str:
    """Remove a meal plan entry."""
    await client.delete_object("meal_plan", entry_id)
    return f"Meal plan entry {entry_id} removed."
