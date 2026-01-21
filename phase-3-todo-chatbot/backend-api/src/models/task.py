from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending", max_length=20)  # "pending", "completed"
    due_date: Optional[datetime] = Field(default=None)


class Task(TaskBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to user
    user: Optional["User"] = Relationship(back_populates="tasks")


class TaskRead(TaskBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
