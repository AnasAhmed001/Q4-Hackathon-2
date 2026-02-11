"""
MCP Tool for Updating Tasks in the Todo AI Chatbot
Implements the update_task functionality for the MCP server.
"""

from typing import Dict, Any, Optional, Union
from mcp.types import Tool as MCPTOOL
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime

from ...database import AsyncSessionFactory
from ...models.task import Task


class UpdateTaskArgs(BaseModel):
    """Arguments for the update_task tool."""
    user_id: str = Field(..., description="The ID of the user updating the task")
    task_id: str = Field(..., description="The ID of the task to update")
    title: Optional[str] = Field(None, description="New title for the task")
    description: Optional[str] = Field(None, description="New description for the task")
    status: Optional[str] = Field(None, description="New task status (pending or completed)")
    due_date: Optional[datetime] = Field(None, description="New due date")
    completed: Optional[bool] = Field(None, description="New completion status (legacy)")


def _coerce_args(args: Union[UpdateTaskArgs, Dict[str, Any]]) -> UpdateTaskArgs:
    if isinstance(args, UpdateTaskArgs):
        return args
    return UpdateTaskArgs.model_validate(args)


def _parse_due_date(value: Optional[Union[str, datetime]]) -> Optional[datetime]:
    if value is None or isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


async def update_task(args: Union[UpdateTaskArgs, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Update an existing task for the specified user.

    Args:
        args: Arguments containing user_id, task_id, and optional fields to update

    Returns:
        Dictionary containing the updated task information
    """
    try:
        args = _coerce_args(args)
        status = args.status
        if args.completed is not None:
            status = "completed" if args.completed else "pending"
        due_date = _parse_due_date(args.due_date)

        async with AsyncSessionFactory() as session:
            # Find the task belonging to the user
            task_result = await session.exec(
                select(Task).where(
                    Task.id == args.task_id,
                    Task.user_id == args.user_id
                )
            )
            task = task_result.first()

            if not task:
                return {
                    "error": f"Task with ID {args.task_id} not found for user {args.user_id}",
                    "success": False
                }

            # Update the task with provided values
            if args.title is not None:
                task.title = args.title
            if args.description is not None:
                task.description = args.description
            if status is not None:
                task.status = status
            if due_date is not None:
                task.due_date = due_date

            # Update the timestamp
            task.updated_at = datetime.utcnow()

            # Commit the changes
            session.add(task)
            await session.commit()
            await session.refresh(task)

            # Return the updated task information
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
                    "updated_at": task.updated_at.isoformat()
                }
            }
    except Exception as e:
        return {
            "error": f"Failed to update task: {str(e)}",
            "success": False
        }


# Define the tool schema for MCP
UPDATE_TASK_TOOL = MCPTOOL(
    name="update_task",
    description="Updates an existing task for the user. Use this when the user wants to modify task details.",
    inputSchema=UpdateTaskArgs.model_json_schema()
)