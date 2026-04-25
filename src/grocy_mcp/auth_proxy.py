"""Small authenticated reverse proxy for the Grocy MCP HTTP endpoint.

This wrapper is intended for deployments where the MCP client can only provide a
URL and cannot set custom headers. Set MCP_ACCESS_TOKEN to require either:

- ?access_token=<token>
- Authorization: Bearer <token>
- X-MCP-Access-Token: <token>

The proxy starts the real grocy-mcp server on localhost and exposes a protected
public listener.
"""

from __future__ import annotations

import asyncio
import os
import signal
import subprocess
import sys
from collections.abc import AsyncIterator

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route


PUBLIC_HOST = os.environ.get("MCP_PROXY_HOST", "0.0.0.0")
PUBLIC_PORT = int(os.environ.get("MCP_PROXY_PORT", "8000"))
BACKEND_HOST = os.environ.get("MCP_BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.environ.get("MCP_BACKEND_PORT", "8001"))
BACKEND_PATH = os.environ.get("MCP_BACKEND_PATH", "/mcp")
ACCESS_TOKEN = os.environ.get("MCP_ACCESS_TOKEN")

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
    "host",
    "content-length",
}

backend_process: subprocess.Popen[str] | None = None
client = httpx.AsyncClient(timeout=None)


def _is_authorised(request: Request) -> bool:
    """Return true when no token is configured or the request presents it."""
    if not ACCESS_TOKEN:
        return True

    query_token = request.query_params.get("access_token")
    if query_token == ACCESS_TOKEN:
        return True

    header_token = request.headers.get("x-mcp-access-token")
    if header_token == ACCESS_TOKEN:
        return True

    auth = request.headers.get("authorization", "")
    return auth == f"Bearer {ACCESS_TOKEN}"


async def _proxy(request: Request) -> Response:
    if not _is_authorised(request):
        return JSONResponse(
            {"error": "unauthorised", "message": "Missing or invalid MCP access token"},
            status_code=401,
        )

    target_url = httpx.URL(
        scheme="http",
        host=BACKEND_HOST,
        port=BACKEND_PORT,
        path=request.url.path,
        query=request.url.query.encode("utf-8"),
    )

    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }

    body = await request.body()
    upstream = client.build_request(
        request.method,
        target_url,
        headers=headers,
        content=body,
    )
    upstream_response = await client.send(upstream, stream=True)

    response_headers = {
        key: value
        for key, value in upstream_response.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }

    async def stream_body() -> AsyncIterator[bytes]:
        try:
            async for chunk in upstream_response.aiter_bytes():
                yield chunk
        finally:
            await upstream_response.aclose()

    return StreamingResponse(
        stream_body(),
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=upstream_response.headers.get("content-type"),
    )


app = Starlette(
    routes=[
        Route("/", _proxy, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]),
        Route("/{path:path}", _proxy, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]),
    ]
)


async def _wait_for_backend() -> None:
    url = f"http://{BACKEND_HOST}:{BACKEND_PORT}{BACKEND_PATH}"
    for _ in range(60):
        try:
            # A GET usually returns 405 for MCP, which is enough to prove it is listening.
            await client.get(url)
            return
        except Exception:
            await asyncio.sleep(0.5)
    raise RuntimeError(f"Backend MCP server did not start at {url}")


async def main() -> None:
    global backend_process

    backend_cmd = [
        "grocy-mcp",
        "--transport",
        "streamable-http",
        "--host",
        BACKEND_HOST,
        "--port",
        str(BACKEND_PORT),
        "--path",
        BACKEND_PATH,
    ]
    backend_process = subprocess.Popen(backend_cmd, text=True)

    def stop_backend(*_: object) -> None:
        if backend_process and backend_process.poll() is None:
            backend_process.terminate()

    signal.signal(signal.SIGTERM, stop_backend)
    signal.signal(signal.SIGINT, stop_backend)

    await _wait_for_backend()

    if ACCESS_TOKEN:
        print("MCP access-token protection enabled", flush=True)
    else:
        print("WARNING: MCP_ACCESS_TOKEN is not set; proxy is allowing all requests", flush=True)

    config = uvicorn.Config(app, host=PUBLIC_HOST, port=PUBLIC_PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

    stop_backend()
    await client.aclose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
