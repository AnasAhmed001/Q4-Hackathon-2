"""
MCP Server for Todo AI Chatbot
Implements MCP tools for task management operations following MCP SDK best practices.
"""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from pydantic import Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


# Lazy import to avoid database connection at import time
def get_database_components():
    from src.database import AsyncSessionFactory, engine
    from src.models.task import Task, TaskCreate, TaskUpdate
    return AsyncSessionFactory, engine, Task, TaskCreate, TaskUpdate


class AppContext:
    """Application context with typed dependencies for the MCP server."""

    def __init__(self, engine):
        self.engine = engine


@asynccontextmanager
async def app_lifespan(server: Server) -> AsyncIterator[Dict[str, Any]]:
    """Manage application lifecycle with lifespan context."""
    # Initialize on startup - engine is already created in database module
    AsyncSessionFactory, engine, _, _, _ = get_database_components()
    try:
        yield {"engine": engine}
    finally:
        # Engine cleanup happens automatically
        pass


# Create low-level MCP server with lifespan management
server = Server("Todo AI Chatbot", lifespan=app_lifespan)


@server.list_tools()
async def list_available_tools() -> List[types.Tool]:
    """List available tools with structured output schemas."""
    return [
        types.Tool(
            name="create_task",
            description="Create a new task for the specified user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Unique identifier of the user"
                    },
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 200,
                        "description": "Title of the task"
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 1000,
                        "description": "Description of the task"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in ISO format (YYYY-MM-DDTHH:MM:SS)"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed"],
                        "default": "pending",
                        "description": "Status of the task"
                    }
                },
                "required": ["user_id", "title"]
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "task": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "user_id": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "status": {"type": "string"},
                            "due_date": {"type": "string"},
                            "created_at": {"type": "string"},
                            "updated_at": {"type": "string"}
                        },
                        "required": ["id", "user_id", "title", "status", "created_at", "updated_at"]
                    },
                    "message": {"type": "string"},
                    "error": {"type": "string"}
                },
                "required": ["success"]
            }
        ),
        types.Tool(
            name="list_tasks",
            description="List tasks for the specified user with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Unique identifier of the user"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed"],
                        "description": "Filter tasks by status"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 1000,
                        "default": 100,
                        "description": "Maximum number of tasks to return"
                    },
                    "offset": {
                        "type": "integer",
                        "minimum": 0,
                        "default": 0,
                        "description": "Number of tasks to skip"
                    }
                },
                "required": ["user_id"]
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "user_id": {"type": "string"},
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "status": {"type": "string"},
                                "due_date": {"type": "string"},
                                "created_at": {"type": "string"},
                                "updated_at": {"type": "string"}
                            },
                            "required": ["id", "user_id", "title", "status", "created_at", "updated_at"]
                        }
                    },
                    "total_count": {"type": "integer"},
                    "returned_count": {"type": "integer"},
                    "filters_applied": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "limit": {"type": "integer"},
                            "offset": {"type": "integer"}
                        }
                    },
                    "message": {"type": "string"},
                    "error": {"type": "string"}
                },
                "required": ["success"]
            }
        ),
        types.Tool(
            name="update_task",
            description="Update an existing task for the specified user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Unique identifier of the user"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Unique identifier of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 200,
                        "description": "New title of the task"
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 1000,
                        "description": "New description of the task"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "New due date in ISO format (YYYY-MM-DDTHH:MM:SS)"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed"],
                        "description": "New status of the task"
                    }
                },
                "required": ["user_id", "task_id"]
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "task": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "user_id": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "status": {"type": "string"},
                            "due_date": {"type": "string"},
                            "created_at": {"type": "string"},
                            "updated_at": {"type": "string"}
                        },
                        "required": ["id", "user_id", "title", "status", "created_at", "updated_at"]
                    },
                    "message": {"type": "string"},
                    "error": {"type": "string"}
                },
                "required": ["success"]
            }
        ),
        types.Tool(
            name="complete_task",
            description="Mark a task as completed for the specified user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Unique identifier of the user"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Unique identifier of the task to mark as completed"
                    }
                },
                "required": ["user_id", "task_id"]
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "task": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "user_id": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "status": {"type": "string"},
                            "due_date": {"type": "string"},
                            "created_at": {"type": "string"},
                            "updated_at": {"type": "string"}
                        },
                        "required": ["id", "user_id", "title", "status", "created_at", "updated_at"]
                    },
                    "message": {"type": "string"},
                    "error": {"type": "string"}
                },
                "required": ["success"]
            }
        ),
        types.Tool(
            name="delete_task",
            description="Delete a task for the specified user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Unique identifier of the user"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Unique identifier of the task to delete"
                    }
                },
                "required": ["user_id", "task_id"]
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "error": {"type": "string"}
                },
                "required": ["success"]
            }
        )
    ]


@server.call_tool()
async def handle_tool_calls(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls with structured output."""
    try:
        if name == "create_task":
            result = await create_task_impl(
                user_id=arguments["user_id"],
                title=arguments["title"],
                description=arguments.get("description"),
                due_date=arguments.get("due_date"),
                status=arguments.get("status", "pending")
            )
        elif name == "list_tasks":
            result = await list_tasks_impl(
                user_id=arguments["user_id"],
                status=arguments.get("status"),
                limit=arguments.get("limit", 100),
                offset=arguments.get("offset", 0)
            )
        elif name == "update_task":
            result = await update_task_impl(
                user_id=arguments["user_id"],
                task_id=arguments["task_id"],
                title=arguments.get("title"),
                description=arguments.get("description"),
                due_date=arguments.get("due_date"),
                status=arguments.get("status")
            )
        elif name == "complete_task":
            result = await complete_task_impl(
                user_id=arguments["user_id"],
                task_id=arguments["task_id"]
            )
        elif name == "delete_task":
            result = await delete_task_impl(
                user_id=arguments["user_id"],
                task_id=arguments["task_id"]
            )
        else:
            raise ValueError(f"Unknown tool: {name}")

        # Return the result as a TextContent block
        return [types.TextContent(type="text", text=str(result))]
    except Exception as e:
        error_result = {"success": False, "error": f"Tool execution failed: {str(e)}"}
        return [types.TextContent(type="text", text=str(error_result))]


async def create_task_impl(user_id: str, title: str, description: Optional[str] = None,
                          due_date: Optional[str] = None, status: str = "pending") -> Dict[str, Any]:
    """
    Implementation for creating a new task for the specified user.

    Args:
        user_id: Unique identifier of the user
        title: Title of the task (required)
        description: Description of the task (optional)
        due_date: Due date in ISO format (optional)
        status: Status of the task (optional, defaults to 'pending')

    Returns:
        Dictionary containing the created task details
    """
    try:
        # Lazy load database components
        AsyncSessionFactory, _, Task, TaskCreate, _ = get_database_components()

        # Parse due_date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid due_date format: {due_date}. Expected ISO format (YYYY-MM-DDTHH:MM:SS)."
                }

        # Create task data
        task_create = TaskCreate(
            title=title,
            description=description,
            due_date=parsed_due_date,
            status=status or "pending"
        )

        # Get database session
        async with AsyncSessionFactory() as session:
            # Create the task in the database
            db_task = await _create_task_for_user(session=session, user_id=user_id, task_create=task_create)

            if db_task:
                return {
                    "success": True,
                    "task": {
                        "id": db_task.id,
                        "user_id": db_task.user_id,
                        "title": db_task.title,
                        "description": db_task.description,
                        "status": db_task.status,
                        "due_date": db_task.due_date.isoformat() if db_task.due_date else None,
                        "created_at": db_task.created_at.isoformat(),
                        "updated_at": db_task.updated_at.isoformat()
                    },
                    "message": f"Task '{db_task.title}' created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create task"
                }

    except IntegrityError as e:
        return {
            "success": False,
            "error": f"Database integrity error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error occurred: {str(e)}"
        }


async def list_tasks_impl(user_id: str, status: Optional[str] = None,
                         limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """
    Implementation for listing tasks for the specified user with optional filtering.

    Args:
        user_id: Unique identifier of the user
        status: Filter tasks by status (optional)
        limit: Maximum number of tasks to return (optional, default 100)
        offset: Number of tasks to skip (optional, default 0)

    Returns:
        Dictionary containing a list of tasks and metadata
    """
    try:
        # Lazy load database components
        AsyncSessionFactory, _, Task, _, _ = get_database_components()

        # Get database session
        async with AsyncSessionFactory() as session:
            # Get tasks from database
            db_tasks = await _get_tasks_by_user(
                session=session,
                user_id=user_id,
                skip=offset,
                limit=limit,
                status=status
            )

            # Get total count
            total_count = await _get_user_tasks_count(session=session, user_id=user_id, status=status)

            # Format tasks
            tasks = []
            for task in db_tasks:
                tasks.append({
                    "id": task.id,
                    "user_id": task.user_id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                })

            return {
                "success": True,
                "tasks": tasks,
                "total_count": total_count,
                "returned_count": len(tasks),
                "filters_applied": {
                    "status": status,
                    "limit": limit,
                    "offset": offset
                },
                "message": f"Retrieved {len(tasks)} tasks for user {user_id}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error retrieving tasks: {str(e)}"
        }


async def update_task_impl(user_id: str, task_id: str, title: Optional[str] = None,
                          description: Optional[str] = None, due_date: Optional[str] = None,
                          status: Optional[str] = None) -> Dict[str, Any]:
    """
    Implementation for updating an existing task for the specified user.

    Args:
        user_id: Unique identifier of the user
        task_id: Unique identifier of the task to update
        title: New title of the task (optional)
        description: New description of the task (optional)
        due_date: New due date in ISO format (optional)
        status: New status of the task (optional)

    Returns:
        Dictionary containing the updated task details
    """
    try:
        # Lazy load database components
        AsyncSessionFactory, _, Task, _, TaskUpdate = get_database_components()

        # Parse due_date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid due_date format: {due_date}. Expected ISO format (YYYY-MM-DDTHH:MM:SS)."
                }

        # Create update data
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if due_date is not None:
            update_data["due_date"] = parsed_due_date
        if status is not None:
            update_data["status"] = status

        task_update = TaskUpdate(**update_data)

        # Get database session
        async with AsyncSessionFactory() as session:
            # Update the task in the database
            db_task = await _update_task_for_user(
                session=session,
                task_id=task_id,
                user_id=user_id,
                task_update=task_update
            )

            if db_task:
                return {
                    "success": True,
                    "task": {
                        "id": db_task.id,
                        "user_id": db_task.user_id,
                        "title": db_task.title,
                        "description": db_task.description,
                        "status": db_task.status,
                        "due_date": db_task.due_date.isoformat() if db_task.due_date else None,
                        "created_at": db_task.created_at.isoformat(),
                        "updated_at": db_task.updated_at.isoformat()
                    },
                    "message": f"Task '{db_task.title}' updated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Task with ID {task_id} not found for user {user_id}"
                }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error updating task: {str(e)}"
        }


async def complete_task_impl(user_id: str, task_id: str) -> Dict[str, Any]:
    """
    Implementation for marking a task as completed for the specified user.

    Args:
        user_id: Unique identifier of the user
        task_id: Unique identifier of the task to mark as completed

    Returns:
        Dictionary indicating success or failure
    """
    try:
        # Lazy load database components
        AsyncSessionFactory, _, Task, _, TaskUpdate = get_database_components()

        # Get database session
        async with AsyncSessionFactory() as session:
            # Update the task status to completed
            db_task = await _update_task_for_user(
                session=session,
                task_id=task_id,
                user_id=user_id,
                task_update=TaskUpdate(status="completed")
            )

            if db_task:
                return {
                    "success": True,
                    "task": {
                        "id": db_task.id,
                        "user_id": db_task.user_id,
                        "title": db_task.title,
                        "description": db_task.description,
                        "status": db_task.status,
                        "due_date": db_task.due_date.isoformat() if db_task.due_date else None,
                        "created_at": db_task.created_at.isoformat(),
                        "updated_at": db_task.updated_at.isoformat()
                    },
                    "message": f"Task '{db_task.title}' marked as completed"
                }
            else:
                return {
                    "success": False,
                    "error": f"Task with ID {task_id} not found for user {user_id}"
                }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error completing task: {str(e)}"
        }


async def delete_task_impl(user_id: str, task_id: str) -> Dict[str, Any]:
    """
    Implementation for deleting a task for the specified user.

    Args:
        user_id: Unique identifier of the user
        task_id: Unique identifier of the task to delete

    Returns:
        Dictionary indicating success or failure
    """
    try:
        # Lazy load database components
        AsyncSessionFactory, _, Task, _, _ = get_database_components()

        # Get database session
        async with AsyncSessionFactory() as session:
            # Delete the task from the database
            deleted = await _delete_task_for_user(
                session=session,
                task_id=task_id,
                user_id=user_id
            )

            if deleted:
                return {
                    "success": True,
                    "message": f"Task with ID {task_id} deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Task with ID {task_id} not found for user {user_id}"
                }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error deleting task: {str(e)}"
        }


# Internal helper functions that mirror the existing CRUD operations
async def _make_naive(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert aware datetimes to naive UTC timestamps for storage."""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


async def _create_task_for_user(*, session: AsyncSession, user_id: str, task_create: 'TaskCreate') -> Optional['Task']:
    """Create a new task for a specific user."""
    try:
        # Lazy load database components
        _, _, Task, _, _ = get_database_components()

        data = task_create.model_dump()
        data["due_date"] = await _make_naive(data.get("due_date"))
        db_task = Task(**data, user_id=user_id)

        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)
        return db_task
    except Exception:
        await session.rollback()
        raise


async def _get_task_by_id(*, session: AsyncSession, task_id: str, user_id: str) -> Optional['Task']:
    """Get a specific task by ID for a specific user."""
    # Lazy load database components
    _, _, Task, _, _ = get_database_components()

    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.exec(statement)
    return result.first()


async def _get_tasks_by_user(*, session: AsyncSession, user_id: str, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List['Task']:
    """Get all tasks for a specific user with optional filtering."""
    # Lazy load database components
    _, _, Task, _, _ = get_database_components()

    statement = select(Task).where(Task.user_id == user_id)

    if status:
        statement = statement.where(Task.status == status)

    statement = statement.offset(skip).limit(limit).order_by(Task.created_at.desc())
    result = await session.exec(statement)
    return result.all()


async def _get_user_tasks_count(*, session: AsyncSession, user_id: str, status: Optional[str] = None) -> int:
    """Get the count of tasks for a specific user."""
    # Lazy load database components
    _, _, Task, _, _ = get_database_components()

    from sqlalchemy import func

    count_statement = select(func.count(Task.id)).where(Task.user_id == user_id)
    if status:
        count_statement = count_statement.where(Task.status == status)

    result = await session.exec(count_statement)
    return result.one()


async def _update_task_for_user(*, session: AsyncSession, task_id: str, user_id: str, task_update: 'TaskUpdate') -> Optional['Task']:
    """Update a specific task for a specific user."""
    # Lazy load database components
    _, _, Task, _, _ = get_database_components()

    db_task = await _get_task_by_id(session=session, task_id=task_id, user_id=user_id)

    if not db_task:
        return None

    # Update only provided fields
    update_data = task_update.model_dump(exclude_unset=True)
    if "due_date" in update_data:
        update_data["due_date"] = await _make_naive(update_data.get("due_date"))
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task


async def _delete_task_for_user(*, session: AsyncSession, task_id: str, user_id: str) -> bool:
    """Delete a specific task for a specific user."""
    # Lazy load database components
    _, _, Task, _, _ = get_database_components()

    db_task = await _get_task_by_id(session=session, task_id=task_id, user_id=user_id)

    if not db_task:
        return False

    await session.delete(db_task)
    await session.commit()
    return True


async def run_server():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="todo-ai-chatbot",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    import sys

    # Run as stdio server by default (for MCP clients that communicate via stdin/stdout)
    if "--stdio" in sys.argv or len(sys.argv) == 1:
        asyncio.run(run_server())
    else:
        # Could extend to support other run modes if needed
        print("Usage: python mcp_server.py [--stdio]")
        sys.exit(1)