"""
MCP Tool Adapters for Cohere V2 API

This module provides:
  1. Cohere-compatible JSON-schema tool definitions
  2. Async executor functions that call the underlying MCP tools
  3. A function map so the chat service can dispatch tool calls by name
"""

from typing import Dict, Any, Optional, List
import json
import os

from src.mcp.tools.create_task import create_task as mcp_create_task
from src.mcp.tools.list_tasks import list_tasks as mcp_list_tasks
from src.mcp.tools.update_task import update_task as mcp_update_task
from src.mcp.tools.complete_task import complete_task as mcp_complete_task
from src.mcp.tools.delete_task import delete_task as mcp_delete_task


# ---------------------------------------------------------------------------
# Cohere V2 tool definitions (JSON-schema format)
# ---------------------------------------------------------------------------

COHERE_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Unique identifier of the user"},
                    "title": {"type": "string", "description": "Title of the task (required)"},
                    "description": {"type": "string", "description": "Description of the task (optional)"},
                    "due_date": {"type": "string", "description": "Due date in ISO format YYYY-MM-DDTHH:MM:SS (optional)"},
                    "status": {"type": "string", "description": "Status of the task, defaults to 'pending'"},
                },
                "required": ["user_id", "title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List tasks for a user with optional status filter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Unique identifier of the user"},
                    "status": {"type": "string", "description": "Filter tasks by status (optional)"},
                    "limit": {"type": "integer", "description": "Maximum number of tasks to return (default 100)"},
                    "offset": {"type": "integer", "description": "Number of tasks to skip (default 0)"},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Unique identifier of the user"},
                    "task_id": {"type": "string", "description": "Unique identifier of the task to update"},
                    "title": {"type": "string", "description": "New title (optional)"},
                    "description": {"type": "string", "description": "New description (optional)"},
                    "due_date": {"type": "string", "description": "New due date in ISO format (optional)"},
                    "status": {"type": "string", "description": "New status (optional)"},
                },
                "required": ["user_id", "task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Unique identifier of the user"},
                    "task_id": {"type": "string", "description": "Unique identifier of the task to complete"},
                },
                "required": ["user_id", "task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task permanently.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Unique identifier of the user"},
                    "task_id": {"type": "string", "description": "Unique identifier of the task to delete"},
                },
                "required": ["user_id", "task_id"],
            },
        },
    },
]


# ---------------------------------------------------------------------------
# Async executor functions (called by the chat-service tool-call loop)
# ---------------------------------------------------------------------------

async def _exec_add_task(**kwargs: Any) -> str:
    try:
        arguments = {
            "user_id": kwargs["user_id"],
            "title": kwargs["title"],
            "description": kwargs.get("description"),
            "due_date": kwargs.get("due_date"),
            "status": kwargs.get("status", "pending"),
        }
        result = await mcp_create_task(arguments)
        if result.get("success") and result.get("task"):
            task = result["task"]
            return json.dumps({"task_id": task.get("id"), "status": "created", "title": task.get("title")})
        return json.dumps({"error": result.get("error", "Unknown error"), "status": "error"})
    except Exception as e:
        return json.dumps({"success": False, "error": f"create_task failed: {e}"})


async def _exec_list_tasks(**kwargs: Any) -> str:
    try:
        status = kwargs.get("status")
        arguments = {
            "user_id": kwargs["user_id"],
            "status": None if status == "all" else status,
            "limit": kwargs.get("limit", 100),
            "offset": kwargs.get("offset", 0),
        }
        result = await mcp_list_tasks(arguments)
        if result.get("success") and result.get("tasks") is not None:
            tasks = [
                {"id": t.get("id"), "title": t.get("title"), "completed": t.get("completed", False)}
                for t in result.get("tasks", [])
            ]
            return json.dumps(tasks)
        return json.dumps({"error": result.get("error", "Unknown error"), "status": "error"})
    except Exception as e:
        return json.dumps({"success": False, "error": f"list_tasks failed: {e}"})


async def _exec_update_task(**kwargs: Any) -> str:
    try:
        arguments = {
            "user_id": kwargs["user_id"],
            "task_id": kwargs["task_id"],
            "title": kwargs.get("title"),
            "description": kwargs.get("description"),
            "due_date": kwargs.get("due_date"),
            "status": kwargs.get("status"),
        }
        result = await mcp_update_task(arguments)
        if result.get("success") and result.get("task"):
            task = result["task"]
            return json.dumps({"task_id": task.get("id"), "status": "updated", "title": task.get("title")})
        return json.dumps({"error": result.get("error", "Unknown error"), "status": "error"})
    except Exception as e:
        return json.dumps({"success": False, "error": f"update_task failed: {e}"})


async def _exec_complete_task(**kwargs: Any) -> str:
    try:
        arguments = {"user_id": kwargs["user_id"], "task_id": kwargs["task_id"]}
        result = await mcp_complete_task(arguments)
        if result.get("success") and result.get("task"):
            task = result["task"]
            return json.dumps({"task_id": task.get("id"), "status": "completed", "title": task.get("title")})
        return json.dumps({"error": result.get("error", "Unknown error"), "status": "error"})
    except Exception as e:
        return json.dumps({"success": False, "error": f"complete_task failed: {e}"})


async def _exec_delete_task(**kwargs: Any) -> str:
    try:
        arguments = {"user_id": kwargs["user_id"], "task_id": kwargs["task_id"]}
        result = await mcp_delete_task(arguments)
        if result.get("success"):
            return json.dumps({"task_id": result.get("task_id"), "status": "deleted", "title": result.get("title")})
        return json.dumps({"error": result.get("error", "Unknown error"), "status": "error"})
    except Exception as e:
        return json.dumps({"success": False, "error": f"delete_task failed: {e}"})


# ---------------------------------------------------------------------------
# Function map: tool-name → async executor
# ---------------------------------------------------------------------------

TOOL_FUNCTIONS = {
    "add_task": _exec_add_task,
    "list_tasks": _exec_list_tasks,
    "update_task": _exec_update_task,
    "complete_task": _exec_complete_task,
    "delete_task": _exec_delete_task,
}