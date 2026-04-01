"""Tests for the meal plan core module."""

from unittest.mock import AsyncMock, patch

from grocy_mcp.core.meal_plan import meal_plan_add, meal_plan_list, meal_plan_remove


async def test_meal_plan_list():
    client = AsyncMock()
    client.get_objects.side_effect = [
        # meal_plan
        [
            {"id": 1, "day": "2026-04-05", "recipe_id": 1, "type": "recipe", "note": ""},
            {"id": 2, "day": "2026-04-06", "recipe_id": None, "type": "note", "note": "Eat out"},
        ],
        # recipes
        [{"id": 1, "name": "Pancakes"}],
    ]
    result = await meal_plan_list(client)
    assert "2026-04-05" in result
    assert "Pancakes" in result
    assert "Eat out" in result
    assert "[1]" in result
    assert "[2]" in result


async def test_meal_plan_list_empty():
    client = AsyncMock()
    client.get_objects.return_value = []
    result = await meal_plan_list(client)
    assert result == "No meal plan entries found."


async def test_meal_plan_add_recipe():
    client = AsyncMock()
    client.create_object.return_value = 10
    with patch("grocy_mcp.core.meal_plan.resolve_recipe", return_value=5):
        result = await meal_plan_add(client, "2026-04-07", recipe="Pancakes")
    client.create_object.assert_called_once_with(
        "meal_plan", {"day": "2026-04-07", "recipe_id": 5, "type": "recipe"}
    )
    assert "2026-04-07" in result
    assert "'Pancakes'" in result


async def test_meal_plan_add_note():
    client = AsyncMock()
    client.create_object.return_value = 11
    result = await meal_plan_add(client, "2026-04-08", note="Leftovers")
    client.create_object.assert_called_once_with(
        "meal_plan", {"day": "2026-04-08", "type": "note", "note": "Leftovers"}
    )
    assert "2026-04-08" in result
    assert "'Leftovers'" in result


async def test_meal_plan_remove():
    client = AsyncMock()
    result = await meal_plan_remove(client, 3)
    client.delete_object.assert_called_once_with("meal_plan", 3)
    assert "3" in result
    assert "removed" in result.lower()
