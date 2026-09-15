# Quickstart Guide: Task Management Backend API

**Feature**: 001-task-management-api
**Date**: 2026-01-13
**Phase**: Phase 1 - Developer Onboarding

## Overview

This guide helps developers set up and start working on the Task Management Backend API. Follow these steps to get the development environment running quickly.

---

## Prerequisites

Before starting, ensure you have:

- **Python**: 3.9 or higher (3.11+ recommended)
- **Poetry**: Dependency management tool (recommended)
- **PostgreSQL**: 12+ or Neon Serverless PostgreSQL account
- **Git**: For version control
- **Docker**: For containerized development (optional but recommended)
- **Code Editor**: VS Code recommended (with Python extensions)

---

## Initial Setup

### 1. Clone and Install Dependencies

```bash
# Navigate to project root
cd backend-api  # or appropriate directory name

# Install dependencies with Poetry
poetry install

# Or with pip (if not using Poetry)
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/task_management_db

# Neon Serverless Configuration (alternative)
NEON_DATABASE_URL=postgresql://username:password@endpoint.neon.tech/dbname

# JWT Configuration
SECRET_KEY=your-secret-key-here-min-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Development/Production
ENVIRONMENT=development
DEBUG=true

# API Configuration
API_PREFIX=/api
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

**Important**: Never commit `.env` to version control. Use `.env.example` as a template.

### 3. Database Setup

```bash
# Apply database migrations
poetry run alembic upgrade head

# Or with pip
python -m alembic upgrade head

# Create initial database tables
python -c "from src.database import create_db_and_tables; create_db_and_tables()"
```

### 4. Verify Setup

```bash
# Run development server
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or with pip
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Open browser to `http://localhost:8000/docs` - you should see the API documentation.

---

## Project Structure

```
backend-api/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database connection and session management
│   ├── models/                 # SQLModel database models
│   │   ├── __init__.py
│   │   ├── user.py            # User model
│   │   └── task.py            # Task model
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── task.py
│   ├── crud/                   # Database operations (Create, Read, Update, Delete)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── task.py
│   ├── auth/                   # Authentication and security utilities
│   │   ├── __init__.py
│   │   ├── jwt.py             # JWT token utilities
│   │   └── security.py        # Security dependencies
│   ├── api/                    # API routes/endpoints
│   │   ├── __init__.py
│   │   ├── deps.py            # Dependency injection
│   │   ├── auth.py            # Authentication endpoints
│   │   └── tasks.py           # Task endpoints
│   └── config/                 # Configuration utilities
│       ├── __init__.py
│       └── settings.py         # Settings management
├── tests/                      # Test files
│   ├── conftest.py            # Test configuration
│   ├── test_auth.py           # Authentication tests
│   ├── test_tasks.py          # Task API tests
│   ├── test_models.py         # Model tests
│   └── test_integration.py    # Integration tests
├── alembic/                    # Database migrations
│   ├── versions/              # Migration files
│   ├── env.py
│   └── script.py.mako
├── requirements/
│   ├── base.txt              # Base dependencies
│   ├── dev.txt               # Development dependencies
│   └── prod.txt              # Production dependencies
├── specs/                     # Feature specifications
│   └── 001-task-management-api/
│       ├── spec.md
│       ├── plan.md
│       ├── research.md
│       ├── data-model.md
│       └── contracts/
│           └── api-spec.openapi.yaml
├── .env.example               # Environment variables template
├── .gitignore
├── alembic.ini               # Alembic configuration
├── poetry.lock               # Poetry lock file
├── pyproject.toml            # Poetry configuration
├── Dockerfile                # Container configuration
└── README.md
```

---

## Development Workflow

### Starting Development Server

```bash
# Start with auto-reload on file changes
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Start with specific workers for production simulation
poetry run uvicorn src.main:app --workers 4 --host 0.0.0.0 --port 8000

# Start with logging
poetry run uvicorn src.main:app --reload --log-level info
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src

# Run specific test file
poetry run pytest tests/test_tasks.py

# Run tests with verbose output
poetry run pytest -v

# Run tests with specific marker
poetry run pytest -m "integration"
```

### Database Operations

```bash
# Create a new migration
poetry run alembic revision --autogenerate -m "Add new field to task table"

# Apply migrations
poetry run alembic upgrade head

# Downgrade to previous version
poetry run alembic downgrade -1

# Check current migration status
poetry run alembic current
```

### Code Quality Checks

```bash
# Run linter
poetry run flake8 src/

# Run formatter
poetry run black src/

# Run type checker
poetry run mypy src/

# Run all checks
poetry run pre-commit run --all-files
```

### Building for Production

```bash
# Build Docker image
docker build -t task-management-api .

# Run in container
docker run -p 8000:8000 task-management-api
```

---

## Key Development Commands

| Command | Purpose |
|---------|---------|
| `poetry run uvicorn src.main:app --reload` | Start development server |
| `poetry run pytest` | Run tests |
| `poetry run alembic upgrade head` | Apply migrations |
| `poetry run black src/` | Format code |
| `poetry run flake8 src/` | Lint code |

---

## Creating New Endpoints

### API Endpoint Example

```python
# src/api/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src import crud, models, schemas
from src.api.deps import get_db, get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=schemas.TaskListResponse)
def read_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    status: str = None
):
    """
    Retrieve user's tasks with optional filtering.
    """
    # Ensure user can only access their own tasks
    tasks = crud.task.get_tasks_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )
    total = crud.task.get_user_tasks_count(db=db, user_id=current_user.id)

    return schemas.TaskListResponse(tasks=tasks, total=total)

@router.post("/", response_model=schemas.CreateTaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: schemas.CreateTaskRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new task for the authenticated user.
    """
    db_task = crud.task.create_task_for_user(
        db=db,
        user_id=current_user.id,
        task=task
    )
    return schemas.CreateTaskResponse(task=db_task, message="Task created successfully")
```

### Database CRUD Example

```python
# src/crud/task.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID

from src.models.task import Task
from src.schemas.task import CreateTaskRequest, UpdateTaskRequest

def get_task_by_id(db: Session, task_id: str, user_id: str) -> Optional[Task]:
    """
    Get a specific task by ID for a specific user.
    """
    return db.query(Task).filter(
        and_(Task.id == task_id, Task.user_id == user_id)
    ).first()

def get_tasks_by_user(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    status: str = None
) -> List[Task]:
    """
    Get all tasks for a specific user with optional filtering.
    """
    query = db.query(Task).filter(Task.user_id == user_id)

    if status:
        query = query.filter(Task.status == status)

    return query.offset(skip).limit(limit).all()

def create_task_for_user(
    db: Session,
    user_id: str,
    task: CreateTaskRequest
) -> Task:
    """
    Create a new task for a specific user.
    """
    db_task = Task(**task.dict(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
```

---

## Authentication Flow

### JWT Token Handling

```python
# src/auth/jwt.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

### Security Dependencies

```python
# src/auth/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src import models, crud
from src.api.deps import get_db
from src.config.settings import settings

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Get current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.user.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    return user
```

---

## API Client Usage

### Using the API

```bash
# Create a new task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Complete project documentation", "description": "Write comprehensive docs", "status": "pending"}'

# Get user's tasks
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Update a task
curl -X PUT http://localhost:8000/api/tasks/TASK_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'

# Delete a task
curl -X DELETE http://localhost:8000/api/tasks/TASK_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Python Client Example

```python
import requests

class TaskAPIClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def get_tasks(self, status: str = None):
        params = {}
        if status:
            params['status'] = status

        response = requests.get(f"{self.base_url}/api/tasks", headers=self.headers, params=params)
        return response.json()

    def create_task(self, title: str, description: str = None, status: str = "pending"):
        data = {"title": title, "description": description, "status": status}
        response = requests.post(f"{self.base_url}/api/tasks", headers=self.headers, json=data)
        return response.json()

    def update_task(self, task_id: str, **kwargs):
        response = requests.put(f"{self.base_url}/api/tasks/{task_id}", headers=self.headers, json=kwargs)
        return response.json()

    def delete_task(self, task_id: str):
        response = requests.delete(f"{self.base_url}/api/tasks/{task_id}", headers=self.headers)
        return response.status_code == 200
```

---

## Testing Guide

### Manual Testing Checklist

Follow the acceptance criteria in `specs/001-task-management-api/spec.md`:

**Authentication Tests**:
- [ ] Login with valid credentials → returns JWT token
- [ ] Login with invalid credentials → returns 401 error
- [ ] Access API without token → returns 401 error
- [ ] Access API with invalid token → returns 401 error

**Task CRUD Tests**:
- [ ] Create task with valid data → returns 201 with created task
- [ ] Create task without authentication → returns 401 error
- [ ] Get user's tasks → returns only user's tasks
- [ ] Get another user's task → returns 403 error
- [ ] Update user's task → returns updated task
- [ ] Update another user's task → returns 403 error
- [ ] Delete user's task → returns success response
- [ ] Delete another user's task → returns 403 error

**User Isolation Tests**:
- [ ] User A cannot see User B's tasks
- [ ] User A cannot modify User B's tasks
- [ ] User A cannot delete User B's tasks
- [ ] Authentication required for all endpoints

**Performance Tests**:
- [ ] Create task completes within 2 seconds (SC-001)
- [ ] Get task list completes within 3 seconds (SC-002)
- [ ] Update task completes within 1 second (SC-003)
- [ ] Delete task completes within 1 second (SC-004)

---

## Common Issues and Solutions

### Issue: "Database connection failed"

**Solution**: Check that PostgreSQL server is running and DATABASE_URL is configured correctly

### Issue: "JWT token invalid"

**Solution**:
1. Check SECRET_KEY in environment variables
2. Verify token hasn't expired
3. Ensure token format is correct (Bearer TOKEN)

### Issue: "User not found" when authenticated

**Solution**: Verify that the user ID in the JWT token exists in the database

### Issue: "Migration failed"

**Solution**:
1. Run `alembic current` to check migration status
2. Run `alembic upgrade head` to apply pending migrations
3. Check migration files for errors

### Issue: "Task not found" for existing task

**Solution**: Ensure you're accessing your own task, not another user's task

---

## Development Best Practices

### 1. Security First

- Always validate user ownership before returning/updating/deleting resources
- Use dependency injection for authentication checks
- Never return sensitive information in API responses
- Validate all input data with Pydantic models

### 2. Type Safety

- Use Pydantic models for all request/response schemas
- Use type hints for all function parameters and return values
- Run mypy regularly to catch type errors

### 3. Error Handling

- Use HTTPException with appropriate status codes
- Provide meaningful error messages to clients
- Log errors server-side for debugging
- Never expose internal system details to clients

### 4. Performance

- Use database indexes appropriately
- Implement pagination for list endpoints
- Use select-in-load for related data when needed
- Monitor query performance with slow query logs

### 5. Testing

- Write unit tests for all business logic
- Write integration tests for API endpoints
- Test authentication and authorization flows
- Test error scenarios and edge cases

---

## Useful Resources

### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

### Project Specs

- Feature Specification: `specs/001-task-management-api/spec.md`
- Implementation Plan: `specs/001-task-management-api/plan.md`
- Data Model: `specs/001-task-management-api/data-model.md`
- API Contracts: `specs/001-task-management-api/contracts/api-spec.openapi.yaml`

### Tools

- [Postman](https://www.postman.com/) - API testing
- [Insomnia](https://insomnia.rest/) - Alternative API client
- [pgAdmin](https://www.pgadmin.org/) - PostgreSQL administration
- [Poetry](https://python-poetry.org/) - Dependency management

---

## Getting Help

### Debugging Steps

1. **Check server logs** for error messages
2. **Verify environment variables** are set correctly
3. **Test database connection** separately
4. **Review the API documentation** at /docs endpoint
5. **Check authentication token** format and validity
6. **Review error responses** for specific details

### Where to Look

- **Authentication errors**: Check `src/auth/` directory
- **Database errors**: Check `src/database.py` and `src/crud/` directory
- **API routing**: Check `src/api/` directory
- **Request validation**: Check `src/schemas/` directory
- **Configuration**: Check `src/config/` directory

---

## Next Steps

After setup is complete:

1. **Review the specification**: Read `specs/001-task-management-api/spec.md`
2. **Study the data model**: Read `specs/001-task-management-api/data-model.md`
3. **Check API contracts**: Review `specs/001-task-management-api/contracts/api-spec.openapi.yaml`
4. **Start implementing**: Follow tasks in `specs/001-task-management-api/tasks.md` (created by `/sp.tasks`)

---

## Quick Reference

### Environment Variables

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/task_management_db
SECRET_KEY=your-32-character-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ENVIRONMENT=development
```

### API Endpoints

- **Authentication**: `/api/auth/login`, `/api/auth/logout`
- **Tasks**: `/api/tasks` (GET, POST), `/api/tasks/{id}` (GET, PUT, DELETE)
- **Docs**: `/docs`, `/redoc`

### Key Files to Know

- `src/main.py` - Application entry point
- `src/database.py` - Database setup
- `src/models/` - Database models
- `src/schemas/` - API schemas
- `src/crud/` - Database operations
- `src/api/` - API routes

---

**Ready to start developing!** 🚀

If you encounter any issues not covered here, check the project specifications or reach out to the team.