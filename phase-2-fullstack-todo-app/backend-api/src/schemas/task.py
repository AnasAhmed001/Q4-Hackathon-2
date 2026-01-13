from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Optional task description")
    status: Optional[TaskStatus] = Field("pending", description="Task status")
    due_date: Optional[datetime] = Field(None, description="Optional due date")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated task title")
    description: Optional[str] = Field(None, max_length=1000, description="Updated task description")
    status: Optional[TaskStatus] = Field(None, description="Updated task status")
    due_date: Optional[datetime] = Field(None, description="Updated due date")


class TaskResponse(TaskBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int


class CreateTaskRequest(TaskBase):
    """Request model for creating a new task"""
    pass


class UpdateTaskRequest(BaseModel):
    """Request model for updating an existing task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated task title")
    description: Optional[str] = Field(None, max_length=1000, description="Updated task description")
    status: Optional[TaskStatus] = Field(None, description="Updated task status")
    due_date: Optional[datetime] = Field(None, description="Updated due date")


class GetTasksResponse(BaseModel):
    """Response model for retrieving user's tasks"""
    tasks: List[TaskResponse]
    total: int
    limit: Optional[int] = None
    offset: Optional[int] = None
