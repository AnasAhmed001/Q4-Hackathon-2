```python
# Full Todo MCP Server for phase-3-todo-chatbot
# Integrates with existing backend-api models/CRUD/DB
# Place in backend-api/src/mcp.py and mount in main.py

import logging
from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager
from pydantic import Field
from sqlmodel.ext.asyncio.session import AsyncSession
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import TextContent

# Project imports (adjust paths)
from src.database import get_async_session
from src.models.task import TaskCreate, TaskUpdate, TaskRead
from src.crud.task import (
    create_task_for_user, get_tasks_by_user, get_user_tasks_count,
    update_task_for_user, delete_task_for_user, get_task_by_id
)
from src.schemas.task import TaskStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    "Todo Chatbot MCP Server",
    stateless_http=True,  # Production stateless
    json_response=True
)

async def get_db_session() -> AsyncSession:
    async for session in get_async_session():
        yield session

@mcp.tool()
async def add_task(
    user_id: str = Field(..., description="User ID (UUID str) to scope the task"),
    title: str = Field(..., min_length=1, max_length=200, description="Task title"),
    description: Optional[str] = Field(None, max_length=1000),
    due_date: Optional[str] = Field(None, description="ISO datetime e.g. '2026-01-27T18:00:00'")
) -> dict:
    \"\"\"Create a new todo task for the user.

    Args:
        user_id: User's unique ID
        title: Required task title
        description: Optional details
        due_date: Optional ISO datetime

    Returns:
        Created task dict {'id', 'title', 'status', ...}

    Example: add_task('550e8400-e29b-41d4-a716-446655440001', 'Buy groceries')
    \"\"\"
    try:
        due = datetime.fromisoformat(due_date.replace('Z', '+00:00')) if due_date else None
        task_create = TaskCreate(title=title, description=description, due_date=due)
        async for session in get_db_session():
            task = await create_task_for_user(session=session, user_id=user_id, task_create=task_create)
        logger.info(f"Added task {task.id} for user {user_id}")
        return TaskRead.from_orm(task).model_dump()
    except Exception as e:
        logger.error(f"Add task failed: {e}")
        raise ValueError(f"Failed to add task: {str(e)}")

@mcp.tool()
async def list_tasks(
    user_id: str = Field(..., description="User ID"),
    limit: int = Field(10, ge=1, le=100),
    offset: int = 0,
    status: Optional[str] = Field(None, description="Filter: 'pending' or 'completed'")
) -> List[dict]:
    \"\"\"List user's tasks with pagination and status filter.

    Returns: List of task dicts + total_count
    Example: list_tasks('user-uuid', limit=5, status='pending')
    \"\"\"
    try:
        async for session in get_db_session():
            tasks = await get_tasks_by_user(session=session, user_id=user_id, skip=offset, limit=limit, status=status)
            count = await get_user_tasks_count(session=session, user_id=user_id, status=status)
        return [TaskRead.from_orm(t).model_dump() for t in tasks]
    except Exception as e:
        raise ValueError(f"Failed to list tasks: {str(e)}")

@mcp.tool()
async def update_task(
    user_id: str,
    task_id: str = Field(..., description="Task ID to update"),
    title: Optional[str] = Field(None, min_length=1, max_length=200),
    description: Optional[str] = Field(None),
    status: Optional[TaskStatus] = Field(None),
    due_date: Optional[str] = Field(None)
) -> Optional[dict]:
    \"\"\"Update existing task.
    Provide any fields to update; unset ignored.
    Returns: Updated task or None if not found.
    \"\"\"
    try:
        due = datetime.fromisoformat(due_date.replace('Z', '+00:00')) if due_date else None
        task_update = TaskUpdate(title=title, description=description, status=status, due_date=due)
        async for session in get_db_session():
            task = await update_task_for_user(session=session, task_id=task_id, user_id=user_id, task_update=task_update)
        if task:
            return TaskRead.from_orm(task).model_dump()
        raise ValueError("Task not found")
    except Exception as e:
        raise ValueError(f"Update failed: {str(e)}")

@mcp.tool()
async def complete_task(
    user_id: str,
    task_id: str = Field(..., description="Task ID to complete")
) -> dict:
    \"\"\"Mark task as completed (status='completed').
    Returns: Updated task.
    \"\"\"
    return await update_task(user_id=user_id, task_id=task_id, status=TaskStatus.COMPLETED)

@mcp.tool()
async def delete_task(
    user_id: str,
    task_id: str = Field(..., description="Task ID to delete")
) -> bool:
    \"\"\"Delete task. Returns True if deleted.
    \"\"\"
    try:
        async for session in get_db_session():
            success = await delete_task_for_user(session=session, task_id=task_id, user_id=user_id)
        if not success:
            raise ValueError("Task not found")
        logger.info(f"Deleted task {task_id}")
        return True
    except Exception as e:
        raise ValueError(f"Delete failed: {str(e)}")

# For FastAPI integration, export mcp.streamable_http_app()
```
