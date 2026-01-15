from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional

from src.auth.jwt_validator import JWTUser
from src.models.task import Task, TaskCreate, TaskUpdate
from src.schemas.task import (
    TaskResponse, TaskListResponse, CreateTaskRequest, 
    UpdateTaskRequest, GetTasksResponse
)
from src.crud.task import (
    create_task_for_user, get_task_by_id, get_tasks_by_user,
    get_user_tasks_count, update_task_for_user, delete_task_for_user
)
from src.api.deps import validate_user_access_dependency, get_db_session

router = APIRouter()


@router.get("/{user_id}/tasks", response_model=GetTasksResponse)
async def read_tasks(
    user_id: str,
    current_user: JWTUser = Depends(validate_user_access_dependency),
    session: AsyncSession = Depends(get_db_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None, regex="^(pending|completed)$")
):
    """Get all tasks for the authenticated user with optional filtering.
    
    Security: user_id in path must match authenticated user's JWT token.
    """
    tasks = await get_tasks_by_user(
        session=session,
        user_id=user_id,
        skip=skip,
        limit=limit,
        status=status
    )
    
    total = await get_user_tasks_count(
        session=session,
        user_id=user_id,
        status=status
    )
    
    return GetTasksResponse(tasks=tasks, total=total, limit=limit, offset=skip)


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_create: CreateTaskRequest,
    current_user: JWTUser = Depends(validate_user_access_dependency),
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new task for the authenticated user.
    
    Security: user_id in path must match authenticated user's JWT token.
    """
    task = await create_task_for_user(
        session=session,
        user_id=user_id,
        task_create=TaskCreate(**task_create.model_dump())
    )
    return task


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def read_task(
    user_id: str,
    task_id: str,
    current_user: JWTUser = Depends(validate_user_access_dependency),
    session: AsyncSession = Depends(get_db_session)
):
    """Get a specific task by ID for the authenticated user.
    
    Security: user_id in path must match authenticated user's JWT token.
    """
    task = await get_task_by_id(
        session=session,
        task_id=task_id,
        user_id=user_id
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or not owned by user"
        )
    
    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: str,
    task_update: UpdateTaskRequest,
    current_user: JWTUser = Depends(validate_user_access_dependency),
    session: AsyncSession = Depends(get_db_session)
):
    """Update a specific task for the authenticated user.
    
    Security: user_id in path must match authenticated user's JWT token.
    """
    task = await update_task_for_user(
        session=session,
        task_id=task_id,
        user_id=user_id,
        task_update=TaskUpdate(**task_update.model_dump(exclude_unset=True))
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or not owned by user"
        )
    
    return task


@router.delete("/{user_id}/tasks/{task_id}")
async def delete_task(
    user_id: str,
    task_id: str,
    current_user: JWTUser = Depends(validate_user_access_dependency),
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a specific task for the authenticated user.
    
    Security: user_id in path must match authenticated user's JWT token.
    """
    success = await delete_task_for_user(
        session=session,
        task_id=task_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or not owned by user"
        )
    
    return {"message": "Task deleted successfully"}
