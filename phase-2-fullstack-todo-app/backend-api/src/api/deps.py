from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.auth.security import get_current_user
from src.models.user import User


async def get_current_user_dependency(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to get the current authenticated user."""
    return current_user


def get_db_session(session: AsyncSession = Depends(get_async_session)) -> AsyncSession:
    """Dependency to get database session."""
    return session
