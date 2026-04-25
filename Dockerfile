FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy the project source and install this fork as the container package.
COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip \
    && pip install .

EXPOSE 8000

# Starts the real FastMCP server on an internal localhost port and exposes an
# authenticated proxy on 0.0.0.0:8000. Set MCP_ACCESS_TOKEN to require either
# ?access_token=<token>, Authorization: Bearer <token>, or X-MCP-Access-Token.
CMD ["python", "-m", "grocy_mcp.auth_proxy"]
