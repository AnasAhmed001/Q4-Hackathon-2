from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import AsyncGenerator

from src.config.settings import settings


# Create async engine for Neon Serverless PostgreSQL
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Set to True for SQL query logging in development
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,  # Recycle connections every 5 minutes
    pool_size=5,  # Initial pool size
    max_overflow=10,  # Max additional connections beyond pool_size
    connect_args={
        "server_settings": {
            "application_name": "task-management-api",
        }
    }
)


# Create async session maker
AsyncSessionFactory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session with proper cleanup."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()


# Function to initialize the database tables
async def create_db_and_tables():
    """Create database tables if they don't exist.
    
    Note: For Neon with Better Auth, tables are managed separately:
    - Better Auth tables: Created via better-auth-schema.sql in Neon console
    - Task tables: Created via Alembic migrations or SQL scripts
    """
    # Tables are managed externally - this is a placeholder
    pass
