from sqlmodel import select
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.task import Task, TaskCreate, TaskUpdate


def _make_naive(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert aware datetimes to naive UTC timestamps for storage."""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


async def create_task_for_user(*, session: AsyncSession, user_id: str, task_create: TaskCreate) -> Task:
    """Create a new task for a specific user."""
    data = task_create.model_dump()
    data["due_date"] = _make_naive(data.get("due_date"))
    db_task = Task(**data, user_id=user_id)

    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task


async def get_task_by_id(*, session: AsyncSession, task_id: str, user_id: str) -> Optional[Task]:
    """Get a specific task by ID for a specific user."""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.exec(statement)
    return result.first()


async def get_tasks_by_user(
    *, 
    session: AsyncSession, 
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
    result = await session.exec(statement)
    return result.all()


async def get_user_tasks_count(*, session: AsyncSession, user_id: str, status: Optional[str] = None) -> int:
    """Get the count of tasks for a specific user."""
    count_statement = select(func.count(Task.id)).where(Task.user_id == user_id)
    if status:
        count_statement = count_statement.where(Task.status == status)

    result = await session.exec(count_statement)
    return result.one()


async def update_task_for_user(*, session: AsyncSession, task_id: str, user_id: str, task_update: TaskUpdate) -> Optional[Task]:
    """Update a specific task for a specific user."""
    db_task = await get_task_by_id(session=session, task_id=task_id, user_id=user_id)

    if not db_task:
        return None

    # Update only provided fields
    update_data = task_update.model_dump(exclude_unset=True)
    if "due_date" in update_data:
        update_data["due_date"] = _make_naive(update_data.get("due_date"))
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task


async def delete_task_for_user(*, session: AsyncSession, task_id: str, user_id: str) -> bool:
    """Delete a specific task for a specific user."""
    db_task = await get_task_by_id(session=session, task_id=task_id, user_id=user_id)

    if not db_task:
        return False

    await session.delete(db_task)
    await session.commit()
    return True
