# Grocy MCP HA Add-on Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship grocy-mcp v0.1.1 with HTTP path support and create a Home Assistant add-on that runs it as a persistent MCP server.

**Architecture:** Two deliverables — (A) add `--path`/`--host` args + `stateless_http` to grocy-mcp's server entry point, bump version, republish to PyPI; (B) create `grocy-mcp-addon` GitHub repo with two-stage Docker build, `start.py` startup script with secret path auth, and HA add-on config files.

**Tech Stack:** Python 3.13, FastMCP 3.2+, Docker (uv builder + python:3.13-slim runtime), HA add-on API (`/data/options.json`), `secrets` stdlib for token generation, `httpx` for connectivity check.

**Spec:** `docs/specs/2026-03-31-grocy-mcp-addon-design.md`

---

## File Map

### Part A — grocy-mcp package (C:\Workspace\grocy-mcp)

| Action | File | Purpose |
|--------|------|---------|
| Modify | `src/grocy_mcp/mcp/server.py:400-423` | Add `--path`, `--host` args; pass `stateless_http=True` |
| Modify | `pyproject.toml:7,24` | Bump version to 0.1.1, bump fastmcp to >=3.2.0 |
| Modify | `tests/test_mcp.py` | Add test for new CLI args |

### Part B — grocy-mcp-addon (C:\Workspace\grocy-mcp-addon)

| Action | File | Purpose |
|--------|------|---------|
| Create | `repository.yaml` | HA add-on repo metadata |
| Create | `grocy-mcp/config.yaml` | Add-on manifest, options schema |
| Create | `grocy-mcp/Dockerfile` | Two-stage build: uv → python slim |
| Create | `grocy-mcp/start.py` | Read config, manage secret, start server |
| Create | `grocy-mcp/translations/en.yaml` | English labels for config UI |
| Create | `grocy-mcp/CHANGELOG.md` | Version history |
| Create | `grocy-mcp/DOCS.md` | In-HA documentation tab |
| Create | `README.md` | Repo overview + install instructions |

---

## Task 1: Add --path and --host args to server.py

**Files:**
- Modify: `C:\Workspace\grocy-mcp\src\grocy_mcp\mcp\server.py:400-423`
- Test: `C:\Workspace\grocy-mcp\tests\test_mcp.py`

- [ ] **Step 1: Write tests for new CLI args**

Add to `tests/test_mcp.py`:

```python
import argparse
from unittest.mock import patch, MagicMock

from grocy_mcp.mcp.server import main, create_mcp_server


def test_main_stdio_default(monkeypatch):
    """Default transport is stdio."""
    server = MagicMock()
    monkeypatch.setattr("grocy_mcp.mcp.server.create_mcp_server", lambda: server)
    monkeypatch.setattr("sys.argv", ["grocy-mcp"])
    main()
    server.run.assert_called_once_with(transport="stdio")


def test_main_http_with_defaults(monkeypatch):
    """HTTP transport passes host, port, path, stateless_http."""
    server = MagicMock()
    monkeypatch.setattr("grocy_mcp.mcp.server.create_mcp_server", lambda: server)
    monkeypatch.setattr("sys.argv", ["grocy-mcp", "--transport", "streamable-http"])
    main()
    server.run.assert_called_once_with(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        path="/mcp",
        stateless_http=True,
    )


def test_main_http_custom_args(monkeypatch):
    """HTTP transport respects --host, --port, --path."""
    server = MagicMock()
    monkeypatch.setattr("grocy_mcp.mcp.server.create_mcp_server", lambda: server)
    monkeypatch.setattr(
        "sys.argv",
        ["grocy-mcp", "--transport", "streamable-http",
         "--host", "127.0.0.1", "--port", "9193", "--path", "/private_abc"],
    )
    main()
    server.run.assert_called_once_with(
        transport="streamable-http",
        host="127.0.0.1",
        port=9193,
        path="/private_abc",
        stateless_http=True,
    )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Workspace/grocy-mcp && python -m pytest tests/test_mcp.py -v`
Expected: FAIL — `main()` doesn't accept `--host` or `--path`, and doesn't pass `stateless_http`.

- [ ] **Step 3: Implement --path and --host in server.py**

Replace `main()` function in `src/grocy_mcp/mcp/server.py` (lines 400-423):

```python
def main() -> None:
    """Entry point for the grocy-mcp MCP server."""
    parser = argparse.ArgumentParser(description="Grocy MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="Transport mechanism (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for streamable-http transport (default: 8000)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Bind address for streamable-http transport (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--path",
        default="/mcp",
        help="MCP endpoint URL path (default: /mcp)",
    )
    args = parser.parse_args()

    server = create_mcp_server()

    if args.transport == "stdio":
        server.run(transport="stdio")
    else:
        server.run(
            transport="streamable-http",
            host=args.host,
            port=args.port,
            path=args.path,
            stateless_http=True,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Workspace/grocy-mcp && python -m pytest tests/test_mcp.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
cd C:/Workspace/grocy-mcp
git add src/grocy_mcp/mcp/server.py tests/test_mcp.py
git commit -m "feat: add --path and --host args with stateless HTTP support"
```

---

## Task 2: Bump version to 0.1.1 and republish to PyPI

**Files:**
- Modify: `C:\Workspace\grocy-mcp\pyproject.toml:7,24`

- [ ] **Step 1: Bump version and fastmcp dependency**

In `pyproject.toml`:
- Line 7: change `version = "0.1.0"` to `version = "0.1.1"`
- Line 24: change `"fastmcp>=2.0"` to `"fastmcp>=3.2.0"`

- [ ] **Step 2: Run full test suite**

Run: `cd C:/Workspace/grocy-mcp && python -m pytest tests/ -v`
Expected: All 62+ tests PASS.

- [ ] **Step 3: Commit version bump**

```bash
cd C:/Workspace/grocy-mcp
git add pyproject.toml
git commit -m "chore: bump version to 0.1.1, require fastmcp>=3.2.0"
```

- [ ] **Step 4: Build and publish to PyPI**

```bash
cd C:/Workspace/grocy-mcp
rm -rf dist/
python -m build
python -m twine check dist/*
python -m twine upload dist/* --username __token__ --password <PYPI_TOKEN>
```

Expected: Both wheel and sdist uploaded successfully.

- [ ] **Step 5: Push both Task 1 and Task 2 commits**

```bash
cd C:/Workspace/grocy-mcp
git push origin main
```

Note: This pushes both the Task 1 commit (server.py changes) and Task 2 commit (version bump) together.

---

## Task 3: Create grocy-mcp-addon repo and scaffold

**Files:**
- Create: `C:\Workspace\grocy-mcp-addon\repository.yaml`
- Create: `C:\Workspace\grocy-mcp-addon\grocy-mcp\config.yaml`
- Create: `C:\Workspace\grocy-mcp-addon\grocy-mcp\translations\en.yaml`
- Create: `C:\Workspace\grocy-mcp-addon\grocy-mcp\CHANGELOG.md`

- [ ] **Step 1: Create GitHub repo**

```bash
cd C:/Workspace
mkdir grocy-mcp-addon
cd grocy-mcp-addon
git init
gh repo create moustafattia/grocy-mcp-addon --public --description "Home Assistant add-on for grocy-mcp" --source .
```

- [ ] **Step 2: Create repository.yaml**

```yaml
name: Grocy MCP Add-on
url: https://github.com/moustafattia/grocy-mcp-addon
maintainer: Moustafa Attia
```

- [ ] **Step 3: Create grocy-mcp/config.yaml**

```yaml
name: "Grocy MCP Server"
description: "MCP server for Grocy — AI agent access to stock, shopping lists, recipes and chores"
version: "0.1.0"
slug: grocy-mcp
url: "https://github.com/moustafattia/grocy-mcp-addon"
init: false
arch:
  - aarch64
  - amd64
icon: mdi:food-variant
startup: application
boot: manual
host_network: true
options:
  grocy_url: "http://homeassistant.local:9192"
  grocy_api_key: ""
  port: 9193
  secret_path: ""
schema:
  grocy_url: str
  grocy_api_key: str
  port: int
  secret_path: str?
```

- [ ] **Step 4: Create grocy-mcp/translations/en.yaml**

```yaml
configuration:
  grocy_url:
    name: Grocy URL
    description: URL of your Grocy instance (e.g. http://homeassistant.local:9192)
  grocy_api_key:
    name: Grocy API Key
    description: API key from Grocy (Settings > Manage API keys)
  port:
    name: Port
    description: HTTP port for the MCP server
  secret_path:
    name: Secret Path
    description: >-
      Custom secret URL path (leave empty to auto-generate).
      Must start with / and be at least 8 characters.
```

- [ ] **Step 5: Create grocy-mcp/CHANGELOG.md**

```markdown
# Changelog

## 0.1.0

- Initial release
- Runs grocy-mcp as stateless HTTP MCP server
- Auto-generated secret path with 128-bit entropy
- Startup connectivity check for Grocy
- Two-stage Docker build (uv + python:3.13-slim)
```

- [ ] **Step 6: Commit scaffold**

```bash
cd C:/Workspace/grocy-mcp-addon
git add repository.yaml grocy-mcp/config.yaml grocy-mcp/translations/en.yaml grocy-mcp/CHANGELOG.md
git commit -m "feat: scaffold HA add-on with config and translations"
```

---

## Task 4: Write Dockerfile

**Files:**
- Create: `C:\Workspace\grocy-mcp-addon\grocy-mcp\Dockerfile`

- [ ] **Step 1: Create Dockerfile**

```dockerfile
# Stage 1: Build
FROM ghcr.io/astral-sh/uv:0.11.0-python3.13-trixie-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_PYTHON_DOWNLOADS=never

WORKDIR /app
RUN uv venv .venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --python .venv/bin/python grocy-mcp==0.1.1

# Stage 2: Runtime
FROM python:3.13-slim

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY start.py /start.py

CMD ["python3", "/start.py"]
```

- [ ] **Step 2: Commit**

```bash
cd C:/Workspace/grocy-mcp-addon
git add grocy-mcp/Dockerfile
git commit -m "feat: add two-stage Dockerfile with uv builder"
```

---

## Task 5: Write start.py

**Files:**
- Create: `C:\Workspace\grocy-mcp-addon\grocy-mcp\start.py`

- [ ] **Step 1: Create start.py**

```python
"""Startup script for the Grocy MCP Home Assistant add-on."""

from __future__ import annotations

import json
import logging
import os
import re
import secrets
import socket
import sys
from pathlib import Path

import httpx

OPTIONS_PATH = Path("/data/options.json")
SECRET_PATH_FILE = Path("/data/secret_path.txt")
SECRET_PATH_RE = re.compile(r"^/(?!.*://)\S{7,}$")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("grocy-mcp-addon")


def read_options() -> dict:
    """Read add-on options from HA Supervisor."""
    if OPTIONS_PATH.exists():
        return json.loads(OPTIONS_PATH.read_text())
    return {}


def generate_secret_path() -> str:
    """Generate a random secret path with 128-bit entropy."""
    return "/private_" + secrets.token_urlsafe(16)


def resolve_secret_path(configured: str) -> str:
    """Resolve the secret path: use configured, load persisted, or generate new."""
    # Use explicitly configured path
    if configured:
        if not SECRET_PATH_RE.match(configured):
            log.error(
                "Invalid secret_path '%s'. Must start with / and be at least 8 characters.",
                configured,
            )
            sys.exit(1)
        SECRET_PATH_FILE.write_text(configured)
        return configured

    # Load persisted path
    if SECRET_PATH_FILE.exists():
        persisted = SECRET_PATH_FILE.read_text().strip()
        if persisted and SECRET_PATH_RE.match(persisted):
            return persisted

    # Generate new path
    new_path = generate_secret_path()
    SECRET_PATH_FILE.write_text(new_path)
    return new_path


def check_grocy_connectivity(url: str, api_key: str) -> None:
    """Check if Grocy is reachable. Logs warning on failure, does not block startup."""
    try:
        resp = httpx.get(
            f"{url.rstrip('/')}/api/system/info",
            headers={"GROCY-API-KEY": api_key},
            timeout=5.0,
        )
        resp.raise_for_status()
        log.info("Grocy is reachable at %s", url)
    except Exception as exc:
        log.warning(
            "Grocy not reachable at %s — tools will fail until Grocy is available. Error: %s",
            url,
            exc,
        )


def main() -> None:
    """Main entry point."""
    options = read_options()

    grocy_url = options.get("grocy_url", "http://homeassistant.local:9192")
    grocy_api_key = options.get("grocy_api_key", "")
    port = options.get("port", 9193)
    secret_path = resolve_secret_path(options.get("secret_path", ""))

    if not grocy_api_key:
        log.error("grocy_api_key is required. Configure it in the add-on options.")
        sys.exit(1)

    # Set env vars for grocy-mcp's load_config()
    os.environ["GROCY_URL"] = grocy_url
    os.environ["GROCY_API_KEY"] = grocy_api_key

    # Startup connectivity check
    check_grocy_connectivity(grocy_url, grocy_api_key)

    # Log the MCP URL
    hostname = socket.gethostname()
    log.info("-----------------------------------------------------------")
    log.info("Grocy MCP Server is running!")
    log.info("MCP endpoint: http://%s:%s%s", hostname, port, secret_path)
    log.info("-----------------------------------------------------------")

    # Import and start the server
    from grocy_mcp.mcp.server import create_mcp_server

    server = create_mcp_server()
    server.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        path=secret_path,
        stateless_http=True,
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
cd C:/Workspace/grocy-mcp-addon
git add grocy-mcp/start.py
git commit -m "feat: add start.py with secret path management and connectivity check"
```

---

## Task 6: Write README and DOCS

**Files:**
- Create: `C:\Workspace\grocy-mcp-addon\README.md`
- Create: `C:\Workspace\grocy-mcp-addon\grocy-mcp\DOCS.md`

- [ ] **Step 1: Create README.md**

```markdown
# Grocy MCP Add-on for Home Assistant

Home Assistant add-on that runs [grocy-mcp](https://github.com/moustafattia/grocy-mcp) as a persistent HTTP MCP server, enabling Claude.ai and other AI agents to manage your Grocy instance remotely.

## Features

- 30 Grocy tools: stock, shopping lists, recipes, chores, system management
- Stateless HTTP MCP transport for Claude.ai compatibility
- Auto-generated secret URL path (128-bit entropy) for security
- Two-stage Docker build for minimal image size

## Installation

1. In Home Assistant, go to **Settings > Add-ons > Add-on Store**
2. Click the overflow menu (top right) > **Repositories**
3. Add: `https://github.com/moustafattia/grocy-mcp-addon`
4. Find **Grocy MCP Server** in the store and install it

## Configuration

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `grocy_url` | Yes | `http://homeassistant.local:9192` | URL of your Grocy instance |
| `grocy_api_key` | Yes | | API key from Grocy (Settings > Manage API keys) |
| `port` | No | `9193` | HTTP port for the MCP server |
| `secret_path` | No | auto-generated | Custom secret URL path |

## Usage with Claude.ai

1. Start the add-on and check the logs for the MCP endpoint URL
2. Add a Cloudflare Tunnel route (e.g. `grocy-mcp.yourdomain.com` -> `http://homeassistant:9193`)
3. In Claude.ai: **Settings > Integrations > Add MCP Server** > paste the full URL

## Links

- [grocy-mcp on PyPI](https://pypi.org/project/grocy-mcp/)
- [grocy-mcp source](https://github.com/moustafattia/grocy-mcp)
```

- [ ] **Step 2: Create grocy-mcp/DOCS.md**

```markdown
# Grocy MCP Server

This add-on runs [grocy-mcp](https://pypi.org/project/grocy-mcp/) as an HTTP MCP server, providing 30 Grocy tools to AI agents like Claude.

## Configuration

### Grocy URL

The URL of your Grocy instance. If Grocy runs as a Home Assistant add-on, use `http://homeassistant.local:9192`.

### Grocy API Key

Generate an API key in Grocy: **Settings > Manage API keys > Add**.

### Port

The HTTP port the MCP server listens on. Default: `9193`. Change only if it conflicts with another service.

### Secret Path

The MCP endpoint includes a secret URL path for security. By default, a random path is auto-generated on first start and persisted across restarts. You can set a custom path (must start with `/` and be at least 8 characters).

## Finding the MCP URL

After starting the add-on, check the **Log** tab. The startup banner shows the full MCP endpoint URL:

```
Grocy MCP Server is running!
MCP endpoint: http://<hostname>:9193/private_abc123...
```

## Remote Access via Cloudflare Tunnel

To use this add-on with Claude.ai, expose it via a Cloudflare Tunnel:

1. In the Cloudflared add-on, add a route: `grocy-mcp.yourdomain.com` -> `http://homeassistant:9193`
2. In Claude.ai: **Settings > Integrations > Add MCP Server**
3. Enter: `https://grocy-mcp.yourdomain.com/private_abc123...`
```

- [ ] **Step 3: Commit**

```bash
cd C:/Workspace/grocy-mcp-addon
git add README.md grocy-mcp/DOCS.md
git commit -m "docs: add README and in-HA documentation"
```

---

## Task 7: Push add-on repo and push grocy-mcp

**Files:** None (git operations only)

- [ ] **Step 1: Push grocy-mcp-addon to GitHub**

```bash
cd C:/Workspace/grocy-mcp-addon
git push -u origin main
```

- [ ] **Step 2: Push grocy-mcp changes to GitHub**

```bash
cd C:/Workspace/grocy-mcp
git push origin main
```

- [ ] **Step 3: Verify both repos on GitHub**

```bash
gh repo view moustafattia/grocy-mcp-addon --web
gh repo view moustafattia/grocy-mcp --web
```
