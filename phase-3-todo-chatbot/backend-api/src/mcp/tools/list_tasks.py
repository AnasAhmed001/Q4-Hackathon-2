"""
MCP Tool for Listing Tasks in the Todo AI Chatbot
Implements the list_tasks functionality for the MCP server.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ...database import AsyncSessionFactory
from ...models.task import Task


class ListTasksArgs(BaseModel):
    """Arguments for the list_tasks tool."""
    user_id: str = Field(..., description="The ID of the user whose tasks to list")
    status: Optional[str] = Field(None, description="Filter by status (pending or completed)")
    completed: Optional[bool] = Field(None, description="Filter by completion status (legacy)")
    limit: int = Field(100, description="Maximum number of tasks to return")
    offset: int = Field(0, description="Number of tasks to skip")


def _coerce_args(args: Union[ListTasksArgs, Dict[str, Any]]) -> ListTasksArgs:
    if isinstance(args, ListTasksArgs):
        return args
    return ListTasksArgs.model_validate(args)


async def list_tasks(args: Union[ListTasksArgs, Dict[str, Any]]) -> Dict[str, Any]:
    """
    List tasks for the specified user with optional filters.

    Args:
        args: Arguments containing user_id, completed filter, limit, and offset

    Returns:
        Dictionary containing the list of tasks
    """
    try:
        args = _coerce_args(args)
        status = args.status
        if args.completed is not None and status is None:
            status = "completed" if args.completed else "pending"

        async with AsyncSessionFactory() as session:
            # Build the query with filters
            query = select(Task).where(Task.user_id == args.user_id)

            if status is not None:
                query = query.where(Task.status == status)

            # Apply limit and offset
            query = query.offset(args.offset).limit(args.limit)

            # Execute the query
            result = await session.exec(query)
            tasks = result.all()

            # Format the results
            task_list = []
            for task in tasks:
                task_dict = {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "completed": task.status == "completed",
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "user_id": task.user_id,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                }
                task_list.append(task_dict)

            # Return the task list
            return {
                "success": True,
                "tasks": task_list,
                "total_count": len(task_list)
            }
    except Exception as e:
        return {
            "error": f"Failed to list tasks: {str(e)}",
            "success": False
        }


from mcp.types import Tool as MCPTOOL

# Define the tool schema for MCP
LIST_TASKS_TOOL = MCPTOOL(
    name="list_tasks",
    description="Lists tasks for the user. Use this when the user wants to see their tasks, optionally filtered by completion status.",
    inputSchema=ListTasksArgs.model_json_schema()
)