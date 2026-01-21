# Data Model: Task Management Backend API

**Feature**: 001-task-management-api
**Date**: 2026-01-13
**Phase**: Phase 1 - Data Model Definition

## Overview

This document defines the data structures and relationships for the Task Management Backend API. The models represent the database schema and align with the functional requirements specified in the feature specification.

---

## Database Entities

### User Entity

Represents an authenticated user in the system.

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Database Columns**:
- `id`: VARCHAR Primary Key (UUID), unique identifier for the user
- `email`: VARCHAR Unique, indexed, user's email address
- `name`: VARCHAR Nullable, optional display name (max 100 chars)
- `created_at`: TIMESTAMP, record creation time
- `updated_at`: TIMESTAMP, last update time

**Validation Rules**:
- `id`: Required, auto-generated UUID
- `email`: Required, valid email format, unique across all users
- `name`: Optional, max 100 characters
- `created_at`: Required, auto-set on creation
- `updated_at`: Required, auto-updated on changes

**Relationships**:
- One user has many tasks (one-to-many relationship)
- Owned by authentication system (external to this model)

**Usage Context**:
- Retrieved from authentication token
- Used for task ownership verification
- Referenced in task records
- Not directly modifiable through task API

---

### Task Entity

Represents a todo task owned by a user.

**SQLModel Definition**:

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid

class Task(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending", max_length=20)  # "pending", "completed"
    due_date: Optional[datetime] = Field(default=None)
    user_id: str = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: Optional["User"] = Relationship(back_populates="tasks")

class User(SQLModel, table=True):
    # ... (previous User definition)
    tasks: list["Task"] = Relationship(back_populates="user")
```

**Database Columns**:
- `id`: VARCHAR Primary Key (UUID), unique task identifier
- `title`: VARCHAR Not Null, task title (1-200 chars)
- `description`: TEXT Nullable, optional task description (max 1000 chars)
- `status`: VARCHAR Not Null, current task status ("pending"/"completed")
- `due_date`: TIMESTAMP Nullable, optional due date
- `user_id`: VARCHAR Foreign Key, references user.id, indexed
- `created_at`: TIMESTAMP, record creation time
- `updated_at`: TIMESTAMP, last update time

**Validation Rules**:
- `id`: Required, auto-generated UUID
- `title`: Required, 1-200 characters, non-empty
- `description`: Optional, max 1000 characters
- `status`: Required, must be "pending" or "completed"
- `due_date`: Optional, if provided must be valid date/time
- `user_id`: Required, must reference valid user
- `created_at`: Required, auto-set on creation
- `updated_at`: Required, auto-updated on changes

**State Transitions**:

```
[pending] → [completed]   (User marks task as done)
[completed] → [pending]   (User reopens task)
```

**Relationships**:
- Many tasks belong to one user (many-to-one)
- Tasks are user-isolated (never shared between users)

**Usage Context**:
- Created through POST /tasks endpoint
- Retrieved through GET /tasks endpoint
- Updated through PUT /tasks/{id} endpoint
- Deleted through DELETE /tasks/{id} endpoint
- Always filtered by authenticated user's ID

---

## API Request/Response Models

### Task Request Models

#### CreateTaskRequest

**Pydantic Definition**:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Optional task description")
    status: Optional[str] = Field("pending", description="Initial task status", pattern="^(pending|completed)$")
    due_date: Optional[datetime] = Field(None, description="Optional due date")
```

**Validation Rules**:
- `title`: Required, 1-200 characters, non-empty
- `description`: Optional, max 1000 characters
- `status`: Optional, default "pending", must be "pending" or "completed"
- `due_date`: Optional, if provided must be valid ISO 8601 date format

---

#### UpdateTaskRequest

**Pydantic Definition**:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UpdateTaskRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated task title")
    description: Optional[str] = Field(None, max_length=1000, description="Updated task description")
    status: Optional[str] = Field(None, description="Updated task status", pattern="^(pending|completed)$")
    due_date: Optional[datetime] = Field(None, description="Updated due date")
```

**Validation Rules**:
- `title`: Optional, if provided 1-200 characters
- `description`: Optional, max 1000 characters
- `status`: Optional, if provided must be "pending" or "completed"
- `due_date`: Optional, if provided must be valid ISO 8601 date format

---

### Task Response Models

#### TaskResponse

**Pydantic Definition**:

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    due_date: Optional[datetime]
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**Fields**:
- `id`: Task unique identifier
- `title`: Task title
- `description`: Task description (may be null)
- `status`: Current status ("pending" or "completed")
- `due_date`: Due date (may be null)
- `user_id`: Owner user ID (internal reference)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

---

#### TaskListResponse

**Pydantic Definition**:

```python
from pydantic import BaseModel
from typing import List

class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
```

**Fields**:
- `tasks`: Array of TaskResponse objects
- `total`: Total count of tasks for the user

---

## Database Schema

### Tables

#### users table
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)
);
```

#### tasks table
```sql
CREATE TABLE tasks (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status ENUM('pending', 'completed') DEFAULT 'pending',
    due_date TIMESTAMP NULL,
    user_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_due_date (due_date),
    INDEX idx_created_at (created_at)
);
```

### Indexes

**Critical Indexes**:
1. `idx_email` on users.email - for authentication lookups
2. `idx_user_id` on tasks.user_id - for user isolation queries
3. `idx_status` on tasks.status - for status filtering
4. `idx_created_at` on tasks.created_at - for ordering and range queries

**Optional Indexes**:
- `idx_due_date` on tasks.due_date - for due date filtering (if needed)

---

## Security Considerations

### Data Isolation

**User Boundary Enforcement**:
- All task queries must include `WHERE user_id = {authenticated_user_id}`
- Foreign key constraint ensures referential integrity
- Cascade delete removes tasks when user is deleted
- No direct access to other users' tasks possible through schema

### Access Control

**Ownership Validation**:
- Every task operation validates user_id matches authenticated user
- Update operations check ownership before modification
- Delete operations verify ownership before deletion
- Read operations filter by user_id to prevent unauthorized access

### Data Protection

**Sensitive Information**:
- No sensitive data stored in task records
- User emails stored but not exposed in task responses
- Internal user_id used for relationships, not exposed to clients
- Audit trails (if needed) stored separately with additional security

---

## Performance Considerations

### Query Optimization

**Efficient Retrieval**:
- Index on user_id enables fast user-specific queries
- Composite indexes for common filter combinations (user_id + status)
- Pagination support for large result sets
- Projection queries to retrieve only needed fields

**Connection Management**:
- Connection pooling for efficient database utilization
- Prepared statements for repeated queries
- Batch operations where appropriate
- Proper disposal of connections in async context

### Scalability Factors

**Data Growth**:
- UUID primary keys prevent conflicts during scaling
- Time-based partitioning possible for historical data
- Index maintenance scheduled during low-usage periods
- Read replicas for query distribution (if needed)

---

## Migration Strategy

### Initial Schema Creation

```python
# Using Alembic for migrations
def upgrade():
    op.create_table('users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(100)),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow),
        sa.Index('idx_email', 'email')
    )

    op.create_table('tasks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.Enum('pending', 'completed'), default='pending'),
        sa.Column('due_date', sa.DateTime),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow),
        sa.Index('idx_user_id', 'user_id'),
        sa.Index('idx_status', 'status')
    )

def downgrade():
    op.drop_table('tasks')
    op.drop_table('users')
```

### Future Extension Points

**Schema Evolution**:
- Add columns using ALTER TABLE (backward compatible)
- New indexes added without affecting existing functionality
- Enum values can be extended (be careful with removals)
- Foreign key relationships can be enhanced

---

## Validation Rules Summary

### Server-Side Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| Task Title | Required, 1-200 chars | "Title is required and must be between 1 and 200 characters" |
| Task Description | Optional, max 1000 chars | "Description must be less than 1000 characters" |
| Task Status | Must be 'pending' or 'completed' | "Status must be 'pending' or 'completed'" |
| User ID | Must reference valid user | "Invalid user ID" |
| Due Date | Optional, valid date format | "Due date must be a valid date" |
| Email | Required, valid format, unique | "Email must be valid and unique" |

### Database Constraints

- NOT NULL constraints on required fields
- UNIQUE constraints on user emails
- FOREIGN KEY constraints for referential integrity
- CHECK constraints for status values (if supported)
- LENGTH constraints for field size limits

---

## API Contract Implications

### Query Parameters

**Filtering Support**:
- `status` (string): Filter by task status ("pending", "completed")
- `limit` (integer): Limit results per page (default 50, max 100)
- `offset` (integer): Offset for pagination
- `sort` (string): Sort order ("created_at", "due_date", "title")

**Search Support**:
- Full-text search on title and description (if database supports)
- Range queries on due_date and created_at
- Combined filters for complex queries

### Response Headers

**Pagination Headers**:
- `X-Total-Count`: Total number of records matching the query
- `X-Limit`: Number of records returned in this response
- `X-Offset`: Offset used for this query

---

## Summary

This data model defines:

✅ **2 Core Entities**: User and Task with proper relationships
✅ **API Models**: Request and response models for all operations
✅ **Database Schema**: Complete table definitions with indexes
✅ **Security Model**: User isolation with foreign key constraints
✅ **Validation Rules**: Comprehensive server and database validation
✅ **Performance Considerations**: Indexing and query optimization
✅ **Migration Strategy**: Version control for schema evolution

Ready for API contract generation (OpenAPI specification).