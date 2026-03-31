# CLAUDE.md

## Project Overview

**grocy-mcp** is an MCP (Model Context Protocol) server and CLI for controlling [Grocy](https://grocy.info/), a self-hosted pantry/household management system. It exposes 30 MCP tools for stock management, shopping lists, recipes, chores, and entity CRUD — usable by AI agents via stdio/HTTP transport or directly via CLI.

## Tech Stack

- **Language**: Python 3.11+
- **MCP Framework**: FastMCP (>=3.2.0)
- **HTTP Client**: httpx (async)
- **CLI Framework**: Typer
- **Data Validation**: Pydantic v2
- **Build System**: Hatchling
- **Test Framework**: pytest + pytest-asyncio + respx (HTTP mocking)
- **Linter/Formatter**: Ruff

## Repository Structure

```
src/grocy_mcp/
├── __init__.py          # Package init, version (0.1.x)
├── client.py            # Async HTTP client wrapping Grocy REST API
├── config.py            # Config resolution: CLI args > env vars > TOML file
├── models.py            # Pydantic models for all Grocy entities
├── exceptions.py        # Typed exception hierarchy (GrocyError base)
├── cli/
│   └── app.py           # Typer CLI with command groups
├── core/                # Business logic (transport-independent)
│   ├── stock.py         # Stock operations (add, consume, transfer, search, etc.)
│   ├── shopping.py      # Shopping list management
│   ├── recipes.py       # Recipe listing, fulfillment, creation
│   ├── chores.py        # Chore tracking and execution
│   ├── system.py        # System info and generic entity CRUD
│   └── resolve.py       # Name-to-ID resolution for products, recipes, etc.
└── mcp/
    └── server.py        # FastMCP server defining 30 tools
tests/
├── conftest.py          # Shared fixtures (base_url, api_key, mock_api)
├── test_client.py       # HTTP client tests
├── test_config.py       # Config loading tests
├── test_mcp.py          # MCP server tool tests
├── test_cli.py          # CLI command tests
├── test_stock.py        # Stock module tests
├── test_shopping.py     # Shopping list tests
├── test_recipes.py      # Recipe tests
├── test_chores.py       # Chore tests
├── test_system.py       # System/entity tests
└── test_resolve.py      # Name resolution tests
docs/specs/              # Design and implementation specs
```

## Common Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest -v

# Run a specific test file
pytest tests/test_stock.py -v

# Lint and format
ruff check src/ tests/
ruff format src/ tests/

# Run MCP server (stdio transport, for Claude Desktop/Code)
grocy-mcp --transport stdio

# Run MCP server (HTTP transport)
grocy-mcp --transport streamable-http --host 0.0.0.0 --port 8000

# Run CLI
grocy stock overview
grocy shopping list
```

## Architecture

**Dual interface, shared core logic:**

1. **`core/`** — Pure business logic modules. Each function takes a `GrocyClient` and returns structured data. No transport coupling.
2. **`mcp/server.py`** — FastMCP tool definitions that call into `core/` modules. Each tool creates a `GrocyClient` from config, calls core logic, and formats the response as a string.
3. **`cli/app.py`** — Typer commands that call into `core/` modules. Same pattern: create client, call core, print output.
4. **`client.py`** — Async HTTP wrapper over the Grocy REST API with retry logic and error mapping.

**Config resolution order** (highest priority first):
1. CLI arguments / function parameters
2. Environment variables (`GROCY_URL`, `GROCY_API_KEY`)
3. TOML config file (`~/.config/grocy-mcp/config.toml`)

## Key Conventions

### Code Style
- **Line length**: 100 characters
- **Target Python version**: 3.11
- **Type annotations**: Used throughout; use `str | None` union syntax (not `Optional`)
- **Imports**: Use `from __future__ import annotations`
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Docstrings**: Google-style on all public functions

### Naming Patterns
- **MCP tool functions**: `{resource}_{action}_tool` (e.g., `stock_add_tool`)
- **Core functions**: `{resource}_{action}` (e.g., `stock_add`)
- **CLI commands**: grouped by resource (e.g., `grocy stock add`)

### Error Handling
- Custom exception hierarchy rooted at `GrocyError` in `exceptions.py`
- Subtypes: `GrocyAuthError`, `GrocyValidationError`, `GrocyNotFoundError`, `GrocyServerError`, `GrocyResolveError`
- Client uses `async with GrocyClient(...)` context manager for cleanup

### Testing
- All I/O is async — tests use `pytest-asyncio` with `asyncio_mode = "auto"`
- HTTP calls mocked with `respx` — no real Grocy instance needed
- Fixtures in `conftest.py`: `base_url`, `api_key`, `mock_api`
- Each core module has a corresponding `test_{module}.py`

### Models
- All Pydantic models use `model_config = {"extra": "allow"}` for forward compatibility with Grocy API changes
- Some models use `populate_by_name = True` for alias support

## Entry Points

Defined in `pyproject.toml`:
- `grocy-mcp` → `grocy_mcp.mcp.server:main` (MCP server)
- `grocy` → `grocy_mcp.cli.app:main` (CLI)

## Dependencies

**Runtime**: fastmcp, httpx, typer, pydantic, platformdirs
**Dev**: pytest, pytest-asyncio, respx, ruff
