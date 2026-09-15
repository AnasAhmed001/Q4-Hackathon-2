"""
MCP Tool for Deleting Tasks in the Todo AI Chatbot
Implements the delete_task functionality for the MCP server.
"""

from typing import Dict, Any, Union
from mcp.types import Tool as MCPTOOL
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


from ...database import AsyncSessionFactory
from ...models.task import Task


class DeleteTaskArgs(BaseModel):
    """Arguments for the delete_task tool."""
    user_id: str = Field(..., description="The ID of the user deleting the task")
    task_id: str = Field(..., description="The ID of the task to delete")


def _coerce_args(args: Union[DeleteTaskArgs, Dict[str, Any]]) -> DeleteTaskArgs:
    if isinstance(args, DeleteTaskArgs):
        return args
    return DeleteTaskArgs.model_validate(args)


async def delete_task(args: Union[DeleteTaskArgs, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Delete an existing task for the specified user.

    Args:
        args: Arguments containing user_id and task_id

    Returns:
        Dictionary indicating success or failure
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

            # Delete the task
            await session.delete(task)
            await session.commit()

            # Return success confirmation
            return {
                "success": True,
                "message": f"Task '{task.title}' has been deleted successfully",
                "task_id": str(task.id),
                "title": task.title
            }
    except Exception as e:
        return {
            "error": f"Failed to delete task: {str(e)}",
            "success": False
        }


# Define the tool schema for MCP
DELETE_TASK_TOOL = MCPTOOL(
    name="delete_task",
    description="Deletes a task for the user. Use this when the user wants to remove a task from their list.",
    inputSchema=DeleteTaskArgs.model_json_schema()
)