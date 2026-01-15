from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.auth.jwt_validator import JWTUser, get_current_user, validate_user_access


async def get_current_user_dependency(current_user: JWTUser = Depends(get_current_user)) -> JWTUser:
    """Dependency to get the current authenticated user from Better Auth JWT."""
    return current_user


async def validate_user_access_dependency(
    user_id: str,
    current_user: JWTUser = Depends(get_current_user)
) -> JWTUser:
    """Dependency to validate user_id in path matches authenticated user."""
    return await validate_user_access(user_id, current_user)


async def get_db_session(session: AsyncSession = Depends(get_async_session)) -> AsyncSession:
    """Dependency to get database session."""
    return session
