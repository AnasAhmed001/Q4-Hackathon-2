from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from sqlalchemy.orm import Session

from src.schemas.user import UserCreate, UserLogin, UserResponse
from src.models.user import User
from src.crud.user import create_user, get_user_by_email, authenticate_user
from src.auth.jwt import create_access_token
from src.database import get_async_session
from src.api.deps import get_current_user_dependency

router = APIRouter()


@router.post("/auth/login", response_model=UserResponse)
async def login_user(user_login: UserLogin, session: Session = Depends(get_async_session)):
    """Authenticate user and return JWT token."""
    user = authenticate_user(session=session, email=user_login.email, password=user_login.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.id}, 
        expires_delta=access_token_expires
    )
    
    return UserResponse(
        user=user,
        token=access_token,
        expires_at=(timedelta(seconds=access_token_expires.total_seconds()) + timedelta(seconds=0))
    )


@router.post("/auth/register", response_model=User)
async def register_user(user_create: UserCreate, session: Session = Depends(get_async_session)):
    """Register a new user."""
    # Check if user already exists
    existing_user = get_user_by_email(session=session, email=user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = create_user(session=session, user_create=user_create)
    return user


@router.post("/auth/logout")
async def logout_user(current_user: User = Depends(get_current_user_dependency)):
    """Logout the current user (client-side token invalidation)."""
    # In a stateless JWT system, logout is typically handled on the client side
    # by discarding the token. However, we can implement server-side token invalidation
    # if needed (e.g., using a blacklist of revoked tokens)
    return {"message": "Successfully logged out"}
