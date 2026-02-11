"""
MCP Tool for Creating Tasks in the Todo AI Chatbot
Implements the create_task functionality for the MCP server.
"""

from typing import Dict, Any, Optional, Union
from mcp.types import Tool as MCPTOOL
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime

from ...database import AsyncSessionFactory
from ...models.task import Task


class CreateTaskArgs(BaseModel):
    """Arguments for the create_task tool."""
    user_id: str = Field(..., description="The ID of the user creating the task")
    title: str = Field(..., description="The title of the task to create")
    description: Optional[str] = Field(None, description="Optional description of the task")
    status: Optional[str] = Field(None, description="Task status (pending or completed)")
    due_date: Optional[datetime] = Field(None, description="Optional due date")
    completed: Optional[bool] = Field(None, description="Whether the task is initially completed (legacy)")


def _coerce_args(args: Union[CreateTaskArgs, Dict[str, Any]]) -> CreateTaskArgs:
    if isinstance(args, CreateTaskArgs):
        return args
    return CreateTaskArgs.model_validate(args)


def _parse_due_date(value: Optional[Union[str, datetime]]) -> Optional[datetime]:
    if value is None or isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


async def create_task(args: Union[CreateTaskArgs, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a new task for the specified user.

    Args:
        args: Arguments containing user_id, title, description, and completed status

    Returns:
        Dictionary containing the created task information
    """
    try:
        args = _coerce_args(args)
        status = args.status
        if args.completed is not None:
            status = "completed" if args.completed else "pending"
        if status is None:
            status = "pending"
        due_date = _parse_due_date(args.due_date)

        async with AsyncSessionFactory() as session:
            # Create a new task
            task = Task(
                title=args.title,
                description=args.description,
                status=status,
                due_date=due_date,
                user_id=args.user_id
            )

            session.add(task)
            await session.commit()
            await session.refresh(task)

            # Return the created task information
            return {
                "success": True,
                "task": {
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
            }
    except Exception as e:
        return {
            "error": f"Failed to create task: {str(e)}",
            "success": False
        }


# Define the tool schema for MCP
CREATE_TASK_TOOL = MCPTOOL(
    name="create_task",
    description="Creates a new task for the user. Use this when the user wants to add a new task to their list.",
    inputSchema=CreateTaskArgs.model_json_schema()
)