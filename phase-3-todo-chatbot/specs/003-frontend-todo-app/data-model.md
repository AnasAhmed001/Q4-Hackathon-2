# Data Model: Frontend Todo Application

**Feature**: 003-frontend-todo-app
**Date**: 2026-01-13
**Phase**: Phase 1 - Data Model Definition

## Overview

This document defines the data structures used in the Frontend Todo Application. These models represent the frontend's view of the data and align with the backend API contracts.

---

## Frontend Data Entities

### User Entity

Represents an authenticated user in the system.

**TypeScript Interface**:

```typescript
interface User {
  id: string;           // Unique user identifier (UUID from backend)
  email: string;        // User's email address
  name?: string;        // Optional display name
  createdAt: string;    // ISO 8601 timestamp
}
```

**Validation Rules**:
- `id`: Required, non-empty string
- `email`: Required, valid email format
- `name`: Optional, max 100 characters
- `createdAt`: Required, ISO 8601 format

**Relationships**:
- One user has many tasks (one-to-many)
- Authenticated via session (managed by Better Auth)

**Usage Context**:
- Returned from authentication endpoints
- Stored in session state
- Used for display in navigation/header
- Not directly modified by frontend (read-only)

---

### Task Entity

Represents a todo task owned by a user.

**TypeScript Interface**:

```typescript
interface Task {
  id: string;                  // Unique task identifier (UUID from backend)
  title: string;               // Task title (required)
  description?: string;        // Optional task description
  status: TaskStatus;          // Current task status
  dueDate?: string;            // Optional due date (ISO 8601)
  userId: string;              // Owner user ID (foreign key)
  createdAt: string;           // Creation timestamp (ISO 8601)
  updatedAt: string;           // Last update timestamp (ISO 8601)
}

type TaskStatus = 'pending' | 'completed';
```

**Validation Rules**:
- `id`: Required, non-empty string (assigned by backend)
- `title`: Required, 1-200 characters, non-empty
- `description`: Optional, max 1000 characters
- `status`: Required, must be 'pending' or 'completed'
- `dueDate`: Optional, ISO 8601 date string, must be future date
- `userId`: Required, non-empty string (auto-assigned from session)
- `createdAt`: Required, ISO 8601 timestamp (assigned by backend)
- `updatedAt`: Required, ISO 8601 timestamp (assigned by backend)

**State Transitions**:

```
[pending] → [completed]   (User marks task as done)
[completed] → [pending]   (User reopens task)
```

**Relationships**:
- Many tasks belong to one user (many-to-one)
- Tasks are user-isolated (never shared between users)

**Usage Context**:
- Displayed in task list view
- Created via task creation form
- Updated via task edit form and status toggle
- Deleted via delete confirmation dialog
- Filtered by status
- Searched by title/description

---

### Session Entity

Represents the authenticated user's session state (managed by Better Auth).

**TypeScript Interface**:

```typescript
interface AuthSession {
  user: User;              // Authenticated user data
  token: string;           // JWT access token
  expiresAt: string;       // Token expiration time (ISO 8601)
}
```

**Validation Rules**:
- `user`: Required, valid User object
- `token`: Required, non-empty JWT string
- `expiresAt`: Required, ISO 8601 timestamp

**Usage Context**:
- Managed by Better Auth library
- Stored in httpOnly cookie (secure)
- Extracted in API client for Authorization header
- Checked by middleware for route protection
- Cleared on logout

---

## Frontend-Only State Models

### UI State Models

These models exist only in the frontend for managing UI state and are not persisted to the backend.

#### TaskListState

**TypeScript Interface**:

```typescript
interface TaskListState {
  tasks: Task[];                    // Current task list
  filteredTasks: Task[];            // Filtered/searched tasks
  isLoading: boolean;               // Loading indicator state
  error: string | null;             // Error message if any
  filter: TaskStatus | 'all';       // Current status filter
  searchQuery: string;              // Current search term
}
```

**Usage**: Manages task list view state, filtering, and search

---

#### TaskFormState

**TypeScript Interface**:

```typescript
interface TaskFormState {
  mode: 'create' | 'edit';          // Form mode
  task: Partial<Task>;              // Task being created/edited
  errors: Record<string, string>;   // Field-level validation errors
  isSubmitting: boolean;            // Submission state
}
```

**Usage**: Manages task creation and edit form state

---

#### DeleteConfirmationState

**TypeScript Interface**:

```typescript
interface DeleteConfirmationState {
  isOpen: boolean;                  // Dialog open state
  taskId: string | null;            // Task to be deleted
  isDeleting: boolean;              // Deletion in progress
}
```

**Usage**: Manages delete confirmation dialog state

---

## API Request/Response Models

### Authentication Requests/Responses

#### Login Request

```typescript
interface LoginRequest {
  email: string;
  password: string;
}
```

#### Login Response

```typescript
interface LoginResponse {
  user: User;
  token: string;
  expiresAt: string;
}
```

#### Logout Response

```typescript
interface LogoutResponse {
  success: boolean;
  message: string;
}
```

---

### Task CRUD Requests/Responses

#### Get Tasks Request

```typescript
// GET /api/tasks
// Query Parameters (optional):
interface GetTasksParams {
  status?: TaskStatus;     // Filter by status
  search?: string;         // Search in title/description
}
```

#### Get Tasks Response

```typescript
interface GetTasksResponse {
  tasks: Task[];
  total: number;
}
```

---

#### Create Task Request

```typescript
// POST /api/tasks
interface CreateTaskRequest {
  title: string;           // Required
  description?: string;    // Optional
  status?: TaskStatus;     // Optional (defaults to 'pending')
  dueDate?: string;        // Optional (ISO 8601)
}
```

#### Create Task Response

```typescript
interface CreateTaskResponse {
  task: Task;              // Newly created task
  message: string;         // Success message
}
```

---

#### Update Task Request

```typescript
// PUT /api/tasks/:id
interface UpdateTaskRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
  dueDate?: string;
}
```

#### Update Task Response

```typescript
interface UpdateTaskResponse {
  task: Task;              // Updated task
  message: string;         // Success message
}
```

---

#### Delete Task Request

```typescript
// DELETE /api/tasks/:id
// No request body
```

#### Delete Task Response

```typescript
interface DeleteTaskResponse {
  success: boolean;
  message: string;
}
```

---

## Error Response Model

All API errors follow a consistent structure:

```typescript
interface ApiErrorResponse {
  error: {
    code: string;          // Error code (e.g., 'UNAUTHORIZED', 'VALIDATION_ERROR')
    message: string;       // Human-readable error message
    details?: Record<string, string>; // Field-specific errors (for validation)
  };
  statusCode: number;      // HTTP status code
}
```

**Standard Error Codes**:
- `UNAUTHORIZED` (401): Authentication required or token invalid
- `FORBIDDEN` (403): User lacks permission for this resource
- `NOT_FOUND` (404): Resource not found
- `VALIDATION_ERROR` (400): Request validation failed
- `INTERNAL_ERROR` (500): Server error

---

## Data Flow Patterns

### Pattern 1: Task List Fetching

```
1. User navigates to /tasks
2. Middleware checks session → valid
3. Page component requests tasks from API client
4. API client adds Authorization header from session
5. Backend returns user's tasks only
6. Frontend displays tasks in list
```

**Data Isolation**: Backend filters by `userId` from JWT token

---

### Pattern 2: Task Creation (Optimistic Update)

```
1. User submits task creation form
2. Frontend validates required fields
3. Frontend adds task to local state (optimistic)
4. API client sends POST request with task data
5. Success: Keep optimistic update, store backend task ID
6. Failure: Remove optimistic task, show error
```

**State Sync**: Local state syncs with backend response

---

### Pattern 3: Task Status Toggle (Optimistic Update)

```
1. User clicks status toggle button
2. Frontend updates task status locally (optimistic)
3. API client sends PUT request with new status
4. Success: Keep optimistic update
5. Failure: Revert to previous status, show error
```

**Performance**: Aligns with SC-004 (update under 3 seconds)

---

### Pattern 4: Task Deletion with Confirmation

```
1. User clicks delete button
2. Frontend shows confirmation dialog
3. User confirms deletion
4. Frontend sends DELETE request
5. Success: Remove task from local state
6. Failure: Show error, keep task in list
```

**No Optimistic Update**: Deletion is destructive, wait for confirmation

---

## Validation Rules Summary

### Client-Side Validation (Immediate Feedback)

| Field | Rule | Error Message |
|-------|------|---------------|
| Task Title | Required, 1-200 chars | "Title is required" / "Title too long (max 200 chars)" |
| Task Description | Optional, max 1000 chars | "Description too long (max 1000 chars)" |
| Task Status | Must be 'pending' or 'completed' | "Invalid status value" |
| Due Date | Optional, ISO 8601, future date | "Due date must be in the future" |
| Email (login) | Required, valid email format | "Valid email required" |
| Password (login) | Required, min 8 chars | "Password must be at least 8 characters" |

### Backend Validation (Defense in Depth)

Backend performs the same validations plus additional security checks:
- User ID matches authenticated user
- Task ownership verification
- Rate limiting
- SQL injection prevention

---

## State Management Strategy

### Local State (React useState/useReducer)

**Used for**:
- Component-specific UI state
- Form input state
- Loading and error states
- Modal/dialog open state

**Not used for**:
- Shared state across components (use props/context)
- Persisted data (use API calls)

---

### Global State (Optional: Zustand if needed)

**Used for**:
- Task list cache (if implementing client-side caching)
- Authentication session state
- Global UI state (theme, notifications)

**Not used for**:
- Component-local state
- Temporary form state

---

## Security Considerations

### Data Protection

1. **No Sensitive Data in State**: Never store passwords or raw tokens in React state
2. **Token in httpOnly Cookie**: JWT managed by Better Auth, not accessible to JavaScript
3. **User Isolation**: All task operations filtered by authenticated user ID
4. **Input Sanitization**: Validate and sanitize all user inputs before API submission

### API Security

1. **Authorization Header**: All protected endpoints require JWT token
2. **Token Expiration**: Handle 401 responses by redirecting to login
3. **CSRF Protection**: Better Auth handles CSRF tokens for state-changing operations
4. **HTTPS Only**: All API requests use HTTPS in production

---

## Performance Considerations

### Data Volume

- **Target**: Support up to 500 tasks per user (SC-010)
- **Strategy**: Client-side filtering and search (no server-side pagination initially)
- **Future Optimization**: Add pagination if task count exceeds 1000

### Caching Strategy

- **Task List**: Cache in memory after fetch, invalidate on mutations
- **No Offline Support**: Per spec constraints, no IndexedDB or localStorage caching
- **Cache Duration**: 5-10 seconds for refresh button

### Bundle Size

- **Target**: Keep page bundle under 200KB (gzipped)
- **Strategy**: Code splitting, tree shaking, dynamic imports for modals
- **Monitoring**: Use Next.js build analyzer

---

## Summary

This data model defines:

✅ **3 Core Entities**: User, Task, Session
✅ **4 UI State Models**: TaskListState, TaskFormState, DeleteConfirmationState
✅ **8 API Models**: Login, Logout, CRUD requests/responses, Error response
✅ **4 Data Flow Patterns**: Fetch, Create, Update, Delete
✅ **Validation Rules**: Client-side and backend validation strategies
✅ **Security Model**: User isolation, token management, input sanitization
✅ **Performance Guidelines**: 500 task support, caching strategy, bundle size

Ready for API contract generation (OpenAPI specification).
