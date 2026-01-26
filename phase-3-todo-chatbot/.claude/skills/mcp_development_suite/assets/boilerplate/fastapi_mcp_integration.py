```python
# Integrate MCP into existing FastAPI app (e.g., backend-api/src/main.py)

from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.routing import Mount
from fastapi import FastAPI  # Existing app
from mcp.server.fastmcp import FastMCP

# Your existing MCP from mcp_server.py
# mcp = FastMCP(...) with tools defined

@asynccontextmanager
async def lifespan(app: FastAPI):
    \"\"\"Lifespan for MCP session manager + DB engine.\"\"\"
    async with mcp.session_manager.run():
        # Existing DB init
        yield

app = FastAPI(...)  # Existing

# Mount MCP at /mcp
app.mount("/mcp", app=mcp.streamable_http_app())

# Run: uvicorn src.main:app --reload
# MCP endpoint: http://localhost:8000/mcp
```
