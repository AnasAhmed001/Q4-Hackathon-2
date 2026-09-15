from sqlmodel import select, Session
from typing import Optional
from src.models.user import User, UserCreate
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """Create a new user with hashed password."""
    hashed_password = get_password_hash(user_create.password)
    
    db_user = User(
        email=user_create.email,
        name=user_create.name,
        hashed_password=hashed_password
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> Optional[User]:
    """Retrieve a user by email."""
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    return user


def get_user_by_id(*, session: Session, user_id: str) -> Optional[User]:
    """Retrieve a user by ID."""
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    return user


def authenticate_user(*, session: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = get_user_by_email(session=session, email=email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
