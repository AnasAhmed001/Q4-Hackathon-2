```python
# Update backend-api/src/main.py to integrate MCP
# Add to existing create_application():

from src.mcp import mcp  # Import the MCP server

@asynccontextmanager
async def lifespan(app: FastAPI):
    \"\"\"Extended lifespan for MCP + existing startup/shutdown.\"\"\"
    # Existing startup
    async with mcp.session_manager.run():  # MCP sessions
        yield
    # Existing shutdown

# In create_application():
app = create_application()
app.mount("/mcp", app=mcp.streamable_http_app())  # Mount at /mcp

# Health check now includes MCP
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mcp_tools": ["add_task", "list_tasks", "update_task", "complete_task", "delete_task"]
    }
```
