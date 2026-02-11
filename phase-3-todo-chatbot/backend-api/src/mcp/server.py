"""
MCP (Model Context Protocol) Server for Todo AI Chatbot
Implements the MCP server that exposes tools for task management operations.
"""

import logging
from typing import Optional

from mcp.server import FastMCP

from .tools.create_task import create_task
from .tools.list_tasks import list_tasks
from .tools.update_task import update_task
from .tools.complete_task import complete_task
from .tools.delete_task import delete_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance using FastMCP
server = FastMCP("todo-ai-chatbot-mcp-server")


@server.tool()
async def create_task_tool(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    status: Optional[str] = None,
    completed: Optional[bool] = None,
):
    """Create a new task for a user."""
    return await create_task(
        {
            "user_id": user_id,
            "title": title,
            "description": description,
            "due_date": due_date,
            "status": status,
            "completed": completed,
        }
    )


@server.tool()
async def list_tasks_tool(
    user_id: str,
    status: Optional[str] = None,
    completed: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
):
    """List tasks for a user."""
    return await list_tasks(
        {
            "user_id": user_id,
            "status": status,
            "completed": completed,
            "limit": limit,
            "offset": offset,
        }
    )


@server.tool()
async def update_task_tool(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    status: Optional[str] = None,
    completed: Optional[bool] = None,
):
    """Update an existing task for a user."""
    return await update_task(
        {
            "user_id": user_id,
            "task_id": task_id,
            "title": title,
            "description": description,
            "due_date": due_date,
            "status": status,
            "completed": completed,
        }
    )


@server.tool()
async def complete_task_tool(user_id: str, task_id: str):
    """Mark a task as completed."""
    return await complete_task({"user_id": user_id, "task_id": task_id})


@server.tool()
async def delete_task_tool(user_id: str, task_id: str):
    """Delete a task."""
    return await delete_task({"user_id": user_id, "task_id": task_id})


def run_mcp_server():
    """Run the MCP server using stdio transport."""
    logger.info("MCP Server running on stdio...")
    server.run("stdio")


if __name__ == "__main__":
    run_mcp_server()