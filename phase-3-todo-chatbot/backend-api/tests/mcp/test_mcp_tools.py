"""
Integration tests for the Todo AI Chatbot MCP tools.
Tests the functionality of all MCP tools for task management operations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlmodel import Session, select
from datetime import datetime

from src.mcp.tools.create_task import create_task, CreateTaskArgs
from src.mcp.tools.list_tasks import list_tasks, ListTasksArgs
from src.mcp.tools.update_task import update_task, UpdateTaskArgs
from src.mcp.tools.complete_task import complete_task, CompleteTaskArgs
from src.mcp.tools.delete_task import delete_task, DeleteTaskArgs
from src.models.task import Task
from src.models.user import User


@pytest.fixture
def mock_session():
    """Mock database session for testing."""
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def sample_user():
    """Sample user for testing."""
    user = User(
        id="user-123",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    return user


@pytest.mark.asyncio
async def test_create_task_success(mock_session, sample_user):
    """Test successful creation of a task."""
    # Arrange
    args = CreateTaskArgs(
        user_id="user-123",
        title="Test Task",
        description="Test Description",
        completed=False
    )

    # Mock the session behavior
    mock_session.exec.return_value.first.return_value = sample_user

    # Act
    result = await create_task(args)

    # Assert
    assert result["success"] is True
    assert result["task"]["title"] == "Test Task"
    assert result["task"]["user_id"] == "user-123"


@pytest.mark.asyncio
async def test_create_task_user_not_found(mock_session):
    """Test creating a task when user doesn't exist."""
    # Arrange
    args = CreateTaskArgs(
        user_id="nonexistent-user",
        title="Test Task",
        description="Test Description",
        completed=False
    )

    # Mock the session behavior
    mock_session.exec.return_value.first.return_value = None

    # Act
    result = await create_task(args)

    # Assert
    assert result["success"] is False
    assert "not found" in result["error"]


@pytest.mark.asyncio
async def test_list_tasks_success(mock_session, sample_user):
    """Test successful listing of tasks."""
    # Arrange
    args = ListTasksArgs(
        user_id="user-123",
        completed=None,
        limit=10,
        offset=0
    )

    # Mock tasks
    mock_task = Task(
        id="task-123",
        title="Test Task",
        description="Test Description",
        completed=False,
        user_id="user-123"
    )

    # Mock the session behavior
    mock_session.exec.return_value.first.return_value = sample_user
    mock_query_result = MagicMock()
    mock_query_result.all.return_value = [mock_task]
    mock_session.exec.return_value = mock_query_result

    # Act
    result = await list_tasks(args)

    # Assert
    assert result["success"] is True
    assert len(result["tasks"]) == 1
    assert result["tasks"][0]["title"] == "Test Task"


@pytest.mark.asyncio
async def test_update_task_success(mock_session, sample_user):
    """Test successful updating of a task."""
    # Arrange
    args = UpdateTaskArgs(
        user_id="user-123",
        task_id="task-123",
        title="Updated Task",
        description="Updated Description",
        completed=True
    )

    # Mock existing task
    existing_task = Task(
        id="task-123",
        title="Original Task",
        description="Original Description",
        completed=False,
        user_id="user-123"
    )

    # Mock the session behavior
    mock_session.exec.return_value.first.side_effect = [sample_user, existing_task]

    # Act
    result = await update_task(args)

    # Assert
    assert result["success"] is True
    assert result["task"]["title"] == "Updated Task"
    assert result["task"]["completed"] is True


@pytest.mark.asyncio
async def test_complete_task_success(mock_session, sample_user):
    """Test successful completion of a task."""
    # Arrange
    args = CompleteTaskArgs(
        user_id="user-123",
        task_id="task-123"
    )

    # Mock existing task
    existing_task = Task(
        id="task-123",
        title="Test Task",
        description="Test Description",
        completed=False,
        user_id="user-123"
    )

    # Mock the session behavior
    mock_session.exec.return_value.first.side_effect = [sample_user, existing_task]

    # Act
    result = await complete_task(args)

    # Assert
    assert result["success"] is True
    assert result["task"]["completed"] is True


@pytest.mark.asyncio
async def test_delete_task_success(mock_session, sample_user):
    """Test successful deletion of a task."""
    # Arrange
    args = DeleteTaskArgs(
        user_id="user-123",
        task_id="task-123"
    )

    # Mock existing task
    existing_task = Task(
        id="task-123",
        title="Test Task",
        description="Test Description",
        completed=False,
        user_id="user-123"
    )

    # Mock the session behavior
    mock_session.exec.return_value.first.side_effect = [sample_user, existing_task]

    # Act
    result = await delete_task(args)

    # Assert
    assert result["success"] is True
    assert "deleted successfully" in result["message"]