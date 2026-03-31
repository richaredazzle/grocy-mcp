"""Tests for name-to-ID resolution."""

from unittest.mock import AsyncMock

import pytest

from grocy_mcp.core.resolve import resolve_entity
from grocy_mcp.exceptions import GrocyResolveError


@pytest.fixture
def mock_client():
    client = AsyncMock()
    client.get_objects.return_value = [
        {"id": 1, "name": "Milk"},
        {"id": 2, "name": "Milk 2%"},
        {"id": 3, "name": "Almond Milk"},
        {"id": 4, "name": "Bread"},
    ]
    return client


async def test_resolve_by_numeric_id(mock_client):
    result = await resolve_entity(mock_client, "products", "4")
    assert result == 4
    mock_client.get_objects.assert_not_called()


async def test_resolve_exact_match(mock_client):
    result = await resolve_entity(mock_client, "products", "Milk")
    assert result == 1


async def test_resolve_exact_match_case_insensitive(mock_client):
    result = await resolve_entity(mock_client, "products", "milk")
    assert result == 1


async def test_resolve_single_substring_match(mock_client):
    result = await resolve_entity(mock_client, "products", "Bread")
    assert result == 4


async def test_resolve_ambiguous_without_exact(mock_client):
    with pytest.raises(GrocyResolveError, match="Multiple"):
        await resolve_entity(mock_client, "products", "ilk")


async def test_resolve_zero_matches(mock_client):
    with pytest.raises(GrocyResolveError, match="No .* found"):
        await resolve_entity(mock_client, "products", "Cheese")
