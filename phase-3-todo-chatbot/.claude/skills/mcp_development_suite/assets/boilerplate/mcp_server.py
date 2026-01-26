```python
# Standalone MCP Server Boilerplate
# Run: python mcp_server.py (stdio) or uvicorn main:app --reload (http)

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional, List, Annotated
from datetime import datetime
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent

# Mock DB - Replace with real SQLModel/Neon
class Task(BaseModel):
    id: str
    title: str
    status: str

mcp = FastMCP(
    "MCP Boilerplate Server",
    stateless_http=True,
    json_response=True  # Production: JSON for agents
)

@mcp.tool()
async def add_task(
    user_id: str = Field(..., description="User UUID to scope tasks"),
    title: str = Field(..., min_length=1, max_length=200, description="Task title"),
    description: Optional[str] = Field(None, max_length=1000),
    due_date: Optional[str] = Field(None, description="ISO datetime YYYY-MM-DDTHH:MM:SSZ")
) -> dict:
    \"\"\"Add new task for user. Returns created task.

    Example: add_task('user-uuid', 'Buy milk', due_date='2026-01-27T18:00:00Z')
    -> {'id': 'task-uuid', 'title': 'Buy milk', 'status': 'pending'}
    \"\"\"
    # TODO: Use real CRUD
    task = Task(id="mock-uuid", title=title, status="pending")
    logging.info(f"Added task {task.id} for user {user_id}")
    return task.model_dump()

@mcp.tool()
async def list_tasks(
    user_id: str,
    limit: int = Field(10, ge=1, le=100),
    status: Optional[str] = Field(None, description="'pending' or 'completed'")
) -> List[dict]:
    \"\"\"List user's tasks with pagination/filter. Returns list of tasks.

    Example: list_tasks('user-uuid', status='pending') -> [{'id': '...', ...}]
    \"\"\"
    # Mock data
    return [{"id": "1", "title": "Mock task", "status": "pending"}]

if __name__ == "__main__":
    # Stdio for local/dev, streamable-http for prod
    mcp.run(transport="streamable-http")  # http://localhost:8000/mcp
```
