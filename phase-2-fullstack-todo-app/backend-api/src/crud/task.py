from sqlmodel import select, Session
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func

from src.models.task import Task, TaskCreate, TaskUpdate


def create_task_for_user(*, session: Session, user_id: str, task_create: TaskCreate) -> Task:
    """Create a new task for a specific user."""
    db_task = Task.model_validate(task_create.model_dump())
    db_task.user_id = user_id
    
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


def get_task_by_id(*, session: Session, task_id: str, user_id: str) -> Optional[Task]:
    """Get a specific task by ID for a specific user."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()
    return task


def get_tasks_by_user(
    *, 
    session: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None
) -> List[Task]:
    """Get all tasks for a specific user with optional filtering."""
    statement = select(Task).where(Task.user_id == user_id)
    
    if status:
        statement = statement.where(Task.status == status)
    
    statement = statement.offset(skip).limit(limit).order_by(Task.created_at.desc())
    tasks = session.exec(statement).all()
    return tasks


def get_user_tasks_count(*, session: Session, user_id: str, status: Optional[str] = None) -> int:
    """Get the count of tasks for a specific user."""
    statement = select(Task).where(Task.user_id == user_id)
    
    if status:
        statement = statement.where(Task.status == status)
    
    count_statement = select(func.count(Task.id)).where(Task.user_id == user_id)
    if status:
        count_statement = count_statement.where(Task.status == status)
    
    result = session.exec(count_statement).one()
    return result


def update_task_for_user(*, session: Session, task_id: str, user_id: str, task_update: TaskUpdate) -> Optional[Task]:
    """Update a specific task for a specific user."""
    db_task = get_task_by_id(session=session, task_id=task_id, user_id=user_id)
    
    if not db_task:
        return None
    
    # Update only provided fields
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db_task.updated_at = datetime.utcnow()
    
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


def delete_task_for_user(*, session: Session, task_id: str, user_id: str) -> bool:
    """Delete a specific task for a specific user."""
    db_task = get_task_by_id(session=session, task_id=task_id, user_id=user_id)
    
    if not db_task:
        return False
    
    session.delete(db_task)
    session.commit()
    return True
