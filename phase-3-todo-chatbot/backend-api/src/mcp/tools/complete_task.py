"""
MCP Tool for Completing Tasks in the Todo AI Chatbot
Implements the complete_task functionality for the MCP server.
"""

from typing import Dict, Any, Union
from mcp.types import Tool as MCPTOOL
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime

from ...database import AsyncSessionFactory
from ...models.task import Task


class CompleteTaskArgs(BaseModel):
    """Arguments for the complete_task tool."""
    user_id: str = Field(..., description="The ID of the user completing the task")
    task_id: str = Field(..., description="The ID of the task to mark as completed")


def _coerce_args(args: Union[CompleteTaskArgs, Dict[str, Any]]) -> CompleteTaskArgs:
    if isinstance(args, CompleteTaskArgs):
        return args
    return CompleteTaskArgs.model_validate(args)


async def complete_task(args: Union[CompleteTaskArgs, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Mark an existing task as completed for the specified user.

    Args:
        args: Arguments containing user_id and task_id

    Returns:
        Dictionary containing the updated task information
    """
    try:
        args = _coerce_args(args)

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

            task.status = "completed"
            task.updated_at = datetime.utcnow()

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
            "error": f"Failed to complete task: {str(e)}",
            "success": False
        }


# Define the tool schema for MCP
COMPLETE_TASK_TOOL = MCPTOOL(
    name="complete_task",
    description="Marks a task as completed for the user. Use this when the user wants to mark a task as done.",
    inputSchema=CompleteTaskArgs.model_json_schema()
)