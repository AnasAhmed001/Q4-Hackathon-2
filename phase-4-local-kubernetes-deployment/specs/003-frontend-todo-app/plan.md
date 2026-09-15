# Implementation Plan: Frontend Todo Application

**Branch**: `003-frontend-todo-app` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-frontend-todo-app/spec.md`

## Summary

Build a responsive Next.js 16 frontend application for task management with secure user authentication, real-time UI updates, and full CRUD operations. The application uses Better Auth for session management, implements optimistic UI updates for fast user feedback, and maintains strict user data isolation through JWT-authenticated API requests.

**Primary Requirement**: Deliver a user-friendly interface for managing tasks with authentication-aware routing and reliable backend API integration.

**Technical Approach**: Next.js 16 App Router with Server/Client component separation, Better Auth for authentication, centralized API client with automatic JWT injection, Tailwind CSS for responsive design, and optimistic UI updates synchronized with backend state.

---

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 16 (React 18+)
**Primary Dependencies**: Next.js 16, React 18, Better Auth, Tailwind CSS
**Storage**: Backend API (PostgreSQL via FastAPI backend)
**Testing**: Manual testing with comprehensive checklist based on acceptance criteria
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge) with responsive support (320px - 2560px)
**Project Type**: Web application (frontend only)
**Performance Goals**:
- Login completion < 30 seconds (SC-001)
- Task creation < 5 seconds (SC-002)
- Status update < 3 seconds (SC-004)
- Error feedback < 2 seconds (SC-006)

**Constraints**:
- No offline support
- No animations or advanced UI effects
- No internationalization
- Frontend must not expose sensitive data (FR-015)
- All API calls must include authentication tokens (FR-003)
- Must support 500 tasks per user (SC-010)

**Scale/Scope**: Single-user interface supporting up to 500 tasks, targeting hackathon demo with 10-20 test users

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Correctness
- **Status**: PASS
- **Verification**: All functional requirements (FR-001 through FR-019) map directly to spec requirements
- **Evidence**: Each FR has corresponding acceptance scenario in spec.md

### ✅ Reliability
- **Status**: PASS
- **Verification**: Error handling for all API failures (FR-013), loading states (FR-017), session stability (FR-016)
- **Evidence**: Data model defines error response structure, API client handles all error codes

### ✅ Simplicity
- **Status**: PASS
- **Verification**: No experimental features, only required functionality from spec
- **Evidence**: Scope explicitly excludes offline support, animations, internationalization

### ✅ User Isolation
- **Status**: PASS
- **Verification**: Backend enforces user filtering (FR-002, FR-003), frontend displays only user's tasks
- **Evidence**: API contracts require JWT token, backend filters by userId from token

### ✅ Security-First
- **Status**: PASS
- **Verification**:
  - Authentication mandatory (FR-001, FR-003, FR-004)
  - JWT in httpOnly cookies (research.md: Security Implementation)
  - No sensitive data exposure (FR-015)
  - Token expiration handling (FR-016)
- **Evidence**: Better Auth manages secure sessions, middleware protects routes, API client includes auth headers

### ✅ Consistency
- **Status**: PASS
- **Verification**: API contracts strictly defined (OpenAPI spec), error responses consistent structure
- **Evidence**: contracts/api-spec.openapi.yaml defines all endpoints, data-model.md defines error format

**Overall Gate Status**: ✅ PASS - Proceed to implementation

---

## Project Structure

### Documentation (this feature)

```text
specs/003-frontend-todo-app/
├── spec.md              # Feature specification (✅ Complete)
├── plan.md              # This file (✅ Complete)
├── research.md          # Phase 0 output (✅ Complete)
├── data-model.md        # Phase 1 output (✅ Complete)
├── quickstart.md        # Phase 1 output (✅ Complete)
├── contracts/           # Phase 1 output (✅ Complete)
│   └── api-spec.openapi.yaml
├── checklists/
│   └── requirements.md  # Spec validation (✅ Complete)
└── tasks.md             # Phase 2 output (⏳ Created by /sp.tasks)
```

### Source Code (repository root)

```text
phase-2-fullstack-todo-app/
├── app/                          # Next.js 16 App Router
│   ├── (auth)/                  # Auth route group (public)
│   │   ├── login/
│   │   │   └── page.tsx         # Login page (Client Component)
│   │   └── layout.tsx           # Auth layout (minimal)
│   ├── (protected)/             # Protected route group (auth required)
│   │   ├── tasks/
│   │   │   ├── page.tsx         # Task list page (Server + Client)
│   │   │   ├── new/
│   │   │   │   └── page.tsx     # Create task page (Client Component)
│   │   │   └── [id]/
│   │   │       ├── page.tsx     # Task detail page (Server + Client)
│   │   │       └── edit/
│   │   │           └── page.tsx # Edit task page (Client Component)
│   │   └── layout.tsx           # Protected layout (nav, user menu)
│   ├── layout.tsx               # Root layout (providers, globals)
│   ├── page.tsx                 # Home page (redirect to /tasks or /login)
│   ├── error.tsx                # Global error boundary
│   └── loading.tsx              # Global loading state
├── components/                   # React components
│   ├── auth/
│   │   ├── LoginForm.tsx        # Login form with validation
│   │   └── LogoutButton.tsx     # Logout action
│   ├── tasks/
│   │   ├── TaskList.tsx         # Task list display (Client)
│   │   ├── TaskCard.tsx         # Individual task card
│   │   ├── TaskForm.tsx         # Create/edit task form
│   │   ├── TaskFilters.tsx      # Status filter + search
│   │   ├── TaskStatusToggle.tsx # Quick status toggle button
│   │   └── DeleteConfirmDialog.tsx # Delete confirmation modal
│   ├── ui/                      # Shared UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Modal.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ErrorMessage.tsx
│   └── layout/
│       ├── Header.tsx           # App header with user info
│       ├── Navbar.tsx           # Navigation menu
│       └── Container.tsx        # Content container
├── lib/                         # Utility libraries
│   ├── api-client.ts            # Centralized API client with auth injection
│   ├── auth.ts                  # Better Auth configuration
│   ├── utils.ts                 # Shared utilities (cn, formatDate, etc.)
│   └── validators.ts            # Input validation functions
├── types/                       # TypeScript type definitions
│   ├── api.ts                   # API request/response types
│   ├── models.ts                # Data model types (User, Task, Session)
│   └── ui.ts                    # UI state types
├── hooks/                       # Custom React hooks
│   ├── useTasks.ts              # Task data fetching and mutations
│   ├── useAuth.ts               # Auth state and actions
│   └── useOptimistic.ts         # Optimistic update helper
├── middleware.ts                # Next.js middleware (route protection)
├── public/                      # Static assets
│   ├── favicon.ico
│   └── images/
├── styles/
│   └── globals.css              # Global styles + Tailwind imports
├── .env.example                 # Environment variable template
├── .env.local                   # Local environment (gitignored)
├── .gitignore
├── next.config.js               # Next.js configuration
├── tailwind.config.js           # Tailwind CSS configuration
├── tsconfig.json                # TypeScript configuration
├── package.json
└── README.md
```

**Structure Decision**: Web application structure with Next.js 16 App Router. Route grouping separates public auth routes from protected task management routes. Component organization follows feature-based structure (auth, tasks, ui, layout). Lib utilities centralize cross-cutting concerns (API, auth, validation).

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations - all constitution checks passed. No complexity justification needed.*

---

## Architecture Overview

### Component Architecture

**Server Components** (default):
- Page layouts
- Task list rendering (initial data fetch)
- Navigation structure
- Static content

**Client Components** (`"use client"`):
- Login form (form state, validation)
- Task creation/edit forms (form state)
- Task list (after initial load - filtering, search, mutations)
- Status toggle buttons (interaction)
- Delete confirmation dialogs (modal state)
- Filters and search inputs

**Rationale**: Server Components reduce JavaScript bundle, improve initial load. Client Components only where interactivity required (forms, buttons, modals).

---

### Authentication Flow

```
1. User visits /tasks (protected route)
2. Middleware checks Better Auth session
3. No session → redirect to /login
4. User submits login form
5. Frontend sends credentials to backend /api/auth/login
6. Backend validates, returns JWT + user data
7. Better Auth stores JWT in httpOnly cookie
8. User redirected to /tasks
9. All subsequent API requests include JWT from cookie
```

**Session Management**:
- JWT stored in httpOnly cookie (XSS protection)
- Middleware validates session on every protected route
- API client extracts JWT from Better Auth session
- 401 responses trigger redirect to login
- Logout clears cookie and redirects to login

---

### API Communication Architecture

**Centralized API Client** (`lib/api-client.ts`):

```typescript
// Pseudo-code structure
class ApiClient {
  baseURL: string

  async request<T>(method, endpoint, data?, options?) {
    // 1. Get JWT from Better Auth session
    const token = await getSessionToken()

    // 2. Build request with Authorization header
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }

    // 3. Make fetch request
    const response = await fetch(baseURL + endpoint, {
      method,
      headers,
      body: data ? JSON.stringify(data) : undefined
    })

    // 4. Handle response
    if (!response.ok) {
      if (response.status === 401) {
        // Token expired or invalid → redirect to login
        redirectToLogin()
      }
      throw await parseError(response)
    }

    return await response.json()
  }

  get<T>(endpoint, options?) { ... }
  post<T>(endpoint, data, options?) { ... }
  put<T>(endpoint, data, options?) { ... }
  delete<T>(endpoint, options?) { ... }
}
```

**Benefits**:
- Single point for auth injection
- Consistent error handling
- Type-safe API calls
- Easy to mock for testing
- Automatic 401 handling

---

### State Management Strategy

**Local Component State** (React useState):
- Form input values
- Modal open/close state
- Component-specific loading states
- Temporary UI state

**Optimistic Updates Pattern**:

```typescript
// Pseudo-code
async function updateTaskStatus(taskId: string, newStatus: TaskStatus) {
  // 1. Optimistically update local state
  setTasks(prev => prev.map(t =>
    t.id === taskId ? { ...t, status: newStatus } : t
  ))

  try {
    // 2. Send API request
    const updatedTask = await apiClient.put(`/tasks/${taskId}`, {
      status: newStatus
    })

    // 3. Success: sync with backend response
    setTasks(prev => prev.map(t =>
      t.id === taskId ? updatedTask : t
    ))
  } catch (error) {
    // 4. Failure: revert to previous state
    setTasks(prev => prev.map(t =>
      t.id === taskId ? { ...t, status: oldStatus } : t
    ))
    showError(error.message)
  }
}
```

**No Global State Library** (initially):
- React state sufficient for task list management
- Better Auth handles auth state
- If complexity grows, consider Zustand (lightweight)

---

### Routing and Middleware

**Route Protection** (`middleware.ts`):

```typescript
// Pseudo-code
export function middleware(request: NextRequest) {
  const session = await getSession(request)
  const isProtectedRoute = request.nextUrl.pathname.startsWith('/tasks')

  if (isProtectedRoute && !session) {
    // Redirect to login with return URL
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('from', request.nextUrl.pathname)
    return NextResponse.redirect(loginUrl)
  }

  if (session && request.nextUrl.pathname === '/login') {
    // Already logged in → redirect to tasks
    return NextResponse.redirect(new URL('/tasks', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/tasks/:path*', '/login']
}
```

**Route Groups**:
- `(auth)`: Public routes (login, signup)
- `(protected)`: Authenticated routes (tasks)
- Separate layouts for different auth contexts

---

### Error Handling Strategy

**Error Boundaries** (`error.tsx` files):
- Route-level error boundaries catch React errors
- Display user-friendly error messages
- Provide recovery actions (retry, go home)

**API Error Handling**:
- 401: Redirect to login (session expired)
- 403: Show "Access Denied" message
- 404: Show "Not Found" message
- 400: Display validation errors inline with form
- 500: Show generic "Something went wrong" with retry

**Loading States** (`loading.tsx` files):
- Route-level loading UI during navigation
- Component-level loading spinners during API calls
- Skeleton screens for task list loading

---

### Responsive Design Strategy

**Tailwind Breakpoints**:
- `default` (mobile-first): 320px - 639px
- `sm`: 640px+
- `md`: 768px+
- `lg`: 1024px+
- `xl`: 1280px+
- `2xl`: 1536px+

**Layout Adaptations**:
- **Mobile (320px - 767px)**:
  - Single column layout
  - Stacked task cards
  - Hamburger menu for navigation
  - Bottom fixed action button

- **Tablet (768px - 1023px)**:
  - Two column layout for task list
  - Sidebar navigation
  - Task cards in grid

- **Desktop (1024px+)**:
  - Three column layout (optional)
  - Persistent sidebar
  - Task cards in grid
  - More compact spacing

**Testing**: Manual testing at 320px, 768px, 1024px, 2560px widths

---

## Implementation Phases

### Phase 0: Research (✅ Complete)

**Output**: `research.md`

**Key Decisions**:
- Next.js 16 with App Router
- Better Auth for authentication
- Centralized API client pattern
- Tailwind CSS for styling
- Optimistic UI updates
- Vercel deployment

---

### Phase 1: Design & Contracts (✅ Complete)

**Output**:
- `data-model.md` - Frontend data entities and validation rules
- `contracts/api-spec.openapi.yaml` - Complete API specification
- `quickstart.md` - Developer onboarding guide

**Key Artifacts**:
- User, Task, Session entities defined
- UI state models (TaskListState, TaskFormState, etc.)
- API request/response types
- Error response structure
- Validation rules and state transitions

---

### Phase 2: Task Generation (⏳ Next Step)

**Command**: `/sp.tasks`

**Expected Output**: `tasks.md` with ordered, testable tasks

**Task Categories** (preview):
1. **Setup Tasks**: Project initialization, dependencies, configuration
2. **Core Infrastructure**: API client, auth setup, middleware
3. **Authentication**: Login page, logout, session management
4. **Task CRUD**: List, create, edit, delete functionality
5. **UI Polish**: Responsive design, loading states, error handling
6. **Testing**: Manual test execution against acceptance criteria

---

## Key Technical Decisions

### Decision 1: Next.js 16 App Router vs Pages Router

**Chosen**: App Router

**Rationale**:
- Server Components reduce bundle size
- Better performance for data fetching
- Simplified route protection with middleware
- Future-proof (Pages Router is legacy)

**Trade-offs**:
- Steeper learning curve
- Some client-side patterns require adjustment

---

### Decision 2: Better Auth vs NextAuth.js

**Chosen**: Better Auth

**Rationale**:
- Simpler setup for our use case
- Better TypeScript support
- More control over session management
- Lightweight compared to NextAuth

**Trade-offs**:
- Smaller community than NextAuth
- Fewer built-in providers (not needed for our case)

---

### Decision 3: Optimistic Updates vs Wait-for-Response

**Chosen**: Optimistic Updates

**Rationale**:
- Better UX (immediate feedback)
- Meets performance goals (SC-002, SC-004)
- Easy to revert on error

**Trade-offs**:
- More complex state management
- Need careful error handling

---

### Decision 4: Manual Testing vs Automated Tests

**Chosen**: Manual Testing (initially)

**Rationale**:
- Faster for hackathon timeline
- Spec provides comprehensive test cases
- Focus resources on features, not test infrastructure

**Trade-offs**:
- Less regression protection
- Requires discipline to test thoroughly

---

## Security Considerations

### Authentication Security

✅ **JWT in httpOnly cookies**: Prevents XSS attacks
✅ **No localStorage tokens**: Avoids common vulnerability
✅ **HTTPS only in production**: Protects token transmission
✅ **Token expiration handling**: Graceful session end
✅ **CSRF protection**: Better Auth handles CSRF tokens

### Data Security

✅ **User isolation**: Backend filters by userId from JWT
✅ **No sensitive data in client state**: Only display data
✅ **No logging of tokens**: Prevent accidental exposure
✅ **Input validation**: Client and server side

### API Security

✅ **Authorization header on all requests**: JWT required
✅ **401/403 handling**: Proper auth/authz enforcement
✅ **Request validation**: Validate all inputs
✅ **Rate limiting**: Backend handles (not frontend concern)

---

## Performance Optimization

### Bundle Size Optimization

- **Code splitting**: Automatic with Next.js pages
- **Dynamic imports**: Lazy load modals and dialogs
- **Tree shaking**: Remove unused Tailwind classes
- **Server Components**: Reduce client-side JavaScript

**Target**: < 200KB initial bundle (gzipped)

### Rendering Optimization

- **Server Components**: Static content rendered on server
- **React.memo()**: Memoize TaskCard components
- **useMemo/useCallback**: Optimize expensive computations
- **Virtual scrolling**: If task list > 100 items (future)

### Network Optimization

- **Optimistic updates**: Reduce perceived latency
- **Request deduplication**: Prevent duplicate API calls
- **Cache task list**: 5-10 second client-side cache
- **Prefetch on hover**: Prefetch task detail pages

---

## Testing Strategy

### Manual Testing Approach

**Primary Testing Method**: Comprehensive checklist based on spec acceptance criteria

**Test Execution**:
1. Set up test environment (local backend + frontend)
2. Create test user accounts (minimum 2 users)
3. Execute each acceptance scenario from spec.md
4. Verify success criteria are met
5. Test edge cases
6. Test responsive design at all breakpoints
7. Document any issues found

**Test Checklist Location**: Will be generated with `/sp.tasks` command

---

### Test Coverage Areas

**Functional Testing** (FR-001 to FR-019):
- ✅ Authentication (login, logout, session)
- ✅ Task CRUD (create, read, update, delete)
- ✅ User isolation (only see own tasks)
- ✅ Filtering and search
- ✅ Form validation
- ✅ Error handling

**Non-Functional Testing**:
- ✅ Performance (meet SC-001 to SC-010)
- ✅ Responsive design (320px to 2560px)
- ✅ Security (no sensitive data exposure)
- ✅ Browser compatibility (Chrome, Firefox, Safari, Edge)

**Edge Case Testing**:
- ✅ Network failures
- ✅ Token expiration
- ✅ Invalid API responses
- ✅ Concurrent operations
- ✅ Very long input strings
- ✅ Empty states (no tasks)

---

## Deployment Strategy

### Platform: Vercel

**Rationale**:
- Built by Next.js creators (best integration)
- Zero configuration deployment
- Automatic preview deployments
- Edge network (fast global access)
- Free tier sufficient for demo

### Deployment Process

1. **Connect GitHub Repository**: Link to Vercel
2. **Configure Environment Variables**:
   - `NEXT_PUBLIC_API_URL`: Backend API URL
   - `AUTH_SECRET`: Secure random string (32+ chars)
   - `AUTH_URL`: Frontend URL
3. **Deploy**: Push to main branch → auto-deploy
4. **Preview**: Pull requests get preview URLs

### Environment Configuration

**Development** (`.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
AUTH_SECRET=dev-secret-min-32-characters-long
AUTH_URL=http://localhost:3000
```

**Production** (Vercel Environment Variables):
```
NEXT_PUBLIC_API_URL=https://api.production-url.com/api
AUTH_SECRET=<secure-random-string>
AUTH_URL=https://todo-app.vercel.app
```

---

## Risk Analysis

### Risk 1: Backend API Compatibility

**Risk**: Frontend API contracts don't match actual backend implementation

**Mitigation**:
- Share OpenAPI spec with backend team early
- Coordinate on data model and endpoints
- Test integration frequently during development
- Use API mocking for frontend-only testing

**Likelihood**: Medium | **Impact**: High

---

### Risk 2: Authentication Integration Complexity

**Risk**: Better Auth integration with backend JWT may have unexpected issues

**Mitigation**:
- Test authentication flow early (first implementation priority)
- Document auth flow clearly
- Have fallback to manual JWT handling if needed
- Coordinate with backend on token format

**Likelihood**: Medium | **Impact**: High

---

### Risk 3: Performance with Large Task Lists

**Risk**: Client-side filtering/search may be slow with 500+ tasks

**Mitigation**:
- Implement client-side caching
- Use React.memo() for task cards
- Monitor performance during testing
- Add pagination if needed (out of initial scope)

**Likelihood**: Low | **Impact**: Medium

---

### Risk 4: Browser Compatibility Issues

**Risk**: Features may not work consistently across browsers

**Mitigation**:
- Use standard Web APIs (avoid experimental features)
- Test on Chrome, Firefox, Safari, Edge
- Use Tailwind CSS (cross-browser compatible)
- Polyfill if needed (Next.js handles most)

**Likelihood**: Low | **Impact**: Low

---

## Dependencies and Assumptions

### External Dependencies

**Backend API**:
- Assumes backend implements endpoints per OpenAPI spec
- Assumes backend enforces user isolation
- Assumes backend returns JWT tokens in expected format
- Assumes backend handles CORS for frontend origin

**Better Auth**:
- Assumes Better Auth supports Next.js 16 App Router
- Assumes JWT extraction API is available
- Assumes httpOnly cookie support

**Deployment**:
- Assumes Vercel account access
- Assumes DNS configuration for custom domain (optional)

### Technical Assumptions

- Node.js 18+ available for development
- Modern browser support (no IE11)
- Backend API is RESTful JSON
- JWT tokens use standard format
- Tailwind CSS v3+ compatibility

---

## Success Metrics (from Spec)

### Functional Success

- ✅ All FR-001 to FR-019 requirements implemented
- ✅ All P1 user stories working (authentication, view, create)
- ✅ All P2 user stories working (update, delete)
- ✅ P3 user story (filter/search) working

### Performance Success

- ✅ SC-001: Login < 30 seconds
- ✅ SC-002: Task creation < 5 seconds
- ✅ SC-003: Responsive 320px - 2560px
- ✅ SC-004: Status update < 3 seconds
- ✅ SC-005: 100% API requests authenticated
- ✅ SC-006: Error messages < 2 seconds
- ✅ SC-007: UI updates < 3 seconds
- ✅ SC-008: User data isolation (no leakage)
- ✅ SC-009: 95% first-task success rate
- ✅ SC-010: Functional with 500 tasks

### Demo Readiness

- ✅ Application runs without errors
- ✅ Authentication flow is smooth
- ✅ Task CRUD operations work reliably
- ✅ UI is visually appealing and responsive
- ✅ Error states are user-friendly
- ✅ Multi-user testing successful

---

## Next Steps

### Immediate Actions

1. **Run `/sp.tasks`**: Generate implementation tasks
2. **Review tasks.md**: Understand task dependencies
3. **Begin implementation**: Start with Phase 0 tasks (setup)
4. **Coordinate with backend**: Share API contracts
5. **Set up development environment**: Follow quickstart.md

### Implementation Order (Preview)

1. **Infrastructure**: Project setup, API client, middleware
2. **Authentication**: Login page, session handling
3. **Core Features**: Task list, create, edit, delete
4. **Polish**: Responsive design, error handling, loading states
5. **Testing**: Execute manual test checklist
6. **Deployment**: Deploy to Vercel for demo

---

## Appendix: File Index

### Planning Documents

- [spec.md](./spec.md) - Feature specification with user stories
- [research.md](./research.md) - Technology decisions and rationale
- [data-model.md](./data-model.md) - Data entities and state models
- [quickstart.md](./quickstart.md) - Developer onboarding guide
- [contracts/api-spec.openapi.yaml](./contracts/api-spec.openapi.yaml) - API specification

### Next Document

- [tasks.md](./tasks.md) - Implementation tasks (generated by `/sp.tasks`)

---

**Plan Status**: ✅ Complete - Ready for task generation

**Last Updated**: 2026-01-13

**Next Command**: `/sp.tasks`
