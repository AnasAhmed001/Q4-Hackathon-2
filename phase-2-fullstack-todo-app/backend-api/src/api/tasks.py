from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from src.models.user import User
from src.models.task import Task, TaskCreate, TaskUpdate
from src.schemas.task import (
    TaskResponse, TaskListResponse, CreateTaskRequest, 
    UpdateTaskRequest, GetTasksResponse
)
from src.crud.task import (
    create_task_for_user, get_task_by_id, get_tasks_by_user,
    get_user_tasks_count, update_task_for_user, delete_task_for_user
)
from src.api.deps import get_current_user_dependency, get_db_session

router = APIRouter()


@router.get("/tasks", response_model=GetTasksResponse)
async def read_tasks(
    current_user: User = Depends(get_current_user_dependency),
    session: Session = Depends(get_db_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None, regex="^(pending|completed)$")
):
    """Get all tasks for the authenticated user with optional filtering."""
    tasks = get_tasks_by_user(
        session=session,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )
    
    total = get_user_tasks_count(
        session=session,
        user_id=current_user.id,
        status=status
    )
    
    return GetTasksResponse(tasks=tasks, total=total, limit=limit, offset=skip)


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_create: CreateTaskRequest,
    current_user: User = Depends(get_current_user_dependency),
    session: Session = Depends(get_db_session)
):
    """Create a new task for the authenticated user."""
    task = create_task_for_user(
        session=session,
        user_id=current_user.id,
        task_create=TaskCreate(**task_create.model_dump())
    )
    return task


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def read_task(
    task_id: str,
    current_user: User = Depends(get_current_user_dependency),
    session: Session = Depends(get_db_session)
):
    """Get a specific task by ID for the authenticated user."""
    task = get_task_by_id(
        session=session,
        task_id=task_id,
        user_id=current_user.id
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or not owned by user"
        )
    
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: UpdateTaskRequest,
    current_user: User = Depends(get_current_user_dependency),
    session: Session = Depends(get_db_session)
):
    """Update a specific task for the authenticated user."""
    task = update_task_for_user(
        session=session,
        task_id=task_id,
        user_id=current_user.id,
        task_update=TaskUpdate(**task_update.model_dump(exclude_unset=True))
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or not owned by user"
        )
    
    return task


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user_dependency),
    session: Session = Depends(get_db_session)
):
    """Delete a specific task for the authenticated user."""
    success = delete_task_for_user(
        session=session,
        task_id=task_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or not owned by user"
        )
    
    return {"message": "Task deleted successfully"}
