# Quickstart Guide: Frontend Todo Application

**Feature**: 003-frontend-todo-app
**Date**: 2026-01-13
**Phase**: Phase 1 - Developer Onboarding

## Overview

This guide helps developers set up and start working on the Frontend Todo Application. Follow these steps to get the development environment running quickly.

---

## Prerequisites

Before starting, ensure you have:

- **Node.js**: v18.17.0 or higher (v20+ recommended)
- **npm**: v9.0.0 or higher (or yarn/pnpm)
- **Git**: For version control
- **Code Editor**: VS Code recommended (with ESLint and Prettier extensions)
- **Backend API**: Running backend API (see backend setup docs)

---

## Initial Setup

### 1. Clone and Install

```bash
# Navigate to project root
cd phase-2-fullstack-todo-app

# Install dependencies
npm install

# or with yarn
yarn install

# or with pnpm
pnpm install
```

### 2. Environment Configuration

Create a `.env.local` file in the project root:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Better Auth Configuration
AUTH_SECRET=your-secret-key-here-min-32-chars
AUTH_URL=http://localhost:3000

# Environment
NODE_ENV=development
```

**Important**: Never commit `.env.local` to version control. Use `.env.example` as a template.

### 3. Verify Setup

```bash
# Run development server
npm run dev

# Server should start at http://localhost:3000
```

Open browser to `http://localhost:3000` - you should see the login page.

---

## Project Structure

```
phase-2-fullstack-todo-app/
├── app/                          # Next.js 16 App Router
│   ├── (auth)/                  # Auth route group
│   │   ├── login/               # Login page
│   │   └── signup/              # Signup page (if implemented)
│   ├── (protected)/             # Protected route group
│   │   └── tasks/               # Task management pages
│   │       ├── page.tsx         # Task list page
│   │       ├── [id]/            # Task detail/edit page
│   │       └── new/             # Create task page
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home/redirect page
│   ├── error.tsx                # Global error boundary
│   └── loading.tsx              # Global loading state
├── components/                   # React components
│   ├── auth/                    # Auth-related components
│   ├── tasks/                   # Task-related components
│   ├── ui/                      # Shared UI components
│   └── layout/                  # Layout components
├── lib/                         # Utility libraries
│   ├── api-client.ts            # Centralized API client
│   ├── auth.ts                  # Better Auth configuration
│   ├── utils.ts                 # Shared utilities
│   └── validators.ts            # Input validation
├── types/                       # TypeScript type definitions
│   ├── api.ts                   # API request/response types
│   ├── models.ts                # Data model types
│   └── ui.ts                    # UI state types
├── middleware.ts                # Next.js middleware (route protection)
├── public/                      # Static assets
├── specs/                       # Feature specifications
│   └── 003-frontend-todo-app/
│       ├── spec.md
│       ├── plan.md
│       ├── research.md
│       ├── data-model.md
│       └── contracts/
└── package.json
```

---

## Development Workflow

### Starting Development Server

```bash
# Start dev server with hot reload
npm run dev

# Start with turbopack (faster)
npm run dev --turbo
```

### Type Checking

```bash
# Run TypeScript type checking
npm run type-check

# Watch mode
npm run type-check -- --watch
```

### Linting and Formatting

```bash
# Run ESLint
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix

# Format with Prettier (if configured)
npm run format
```

### Building for Production

```bash
# Create production build
npm run build

# Start production server locally
npm run start
```

---

## Key Development Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start development server |
| `npm run build` | Create production build |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run type-check` | Run TypeScript compiler check |

---

## Creating New Components

### Client Component Example

```typescript
// components/tasks/TaskCard.tsx
'use client'

import { Task } from '@/types/models'
import { useState } from 'react'

interface TaskCardProps {
  task: Task
  onUpdate: (task: Task) => void
  onDelete: (id: string) => void
}

export function TaskCard({ task, onUpdate, onDelete }: TaskCardProps) {
  const [isEditing, setIsEditing] = useState(false)

  // Component logic here

  return (
    <div className="border rounded-lg p-4">
      {/* Component JSX */}
    </div>
  )
}
```

### Server Component Example

```typescript
// app/(protected)/tasks/page.tsx
import { getTasks } from '@/lib/api-client'
import { TaskList } from '@/components/tasks/TaskList'

export default async function TasksPage() {
  // Fetch data on server
  const tasks = await getTasks()

  return (
    <div>
      <h1>My Tasks</h1>
      <TaskList tasks={tasks} />
    </div>
  )
}
```

---

## API Client Usage

### Making API Calls

```typescript
// lib/api-client.ts usage example
import { apiClient } from '@/lib/api-client'
import { Task, CreateTaskRequest } from '@/types/api'

// GET request
const tasks = await apiClient.get<Task[]>('/tasks')

// POST request
const newTask = await apiClient.post<Task, CreateTaskRequest>('/tasks', {
  title: 'New Task',
  description: 'Task description',
  status: 'pending'
})

// PUT request
const updatedTask = await apiClient.put<Task>(`/tasks/${id}`, {
  status: 'completed'
})

// DELETE request
await apiClient.delete(`/tasks/${id}`)
```

### Error Handling

```typescript
try {
  const tasks = await apiClient.get<Task[]>('/tasks')
  // Handle success
} catch (error) {
  if (error.statusCode === 401) {
    // Handle authentication error
    redirectToLogin()
  } else if (error.statusCode === 403) {
    // Handle authorization error
    showForbiddenMessage()
  } else {
    // Handle other errors
    showErrorMessage(error.message)
  }
}
```

---

## Authentication Flow

### Checking Auth Status

```typescript
// In Server Component
import { auth } from '@/lib/auth'

export default async function ProtectedPage() {
  const session = await auth()

  if (!session) {
    redirect('/login')
  }

  return <div>Welcome, {session.user.email}</div>
}
```

### Protecting Routes with Middleware

```typescript
// middleware.ts (already configured)
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Check authentication
  const token = request.cookies.get('auth-token')

  if (!token && request.nextUrl.pathname.startsWith('/tasks')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/tasks/:path*']
}
```

---

## Testing Guide

### Manual Testing Checklist

Follow the acceptance criteria in `specs/003-frontend-todo-app/spec.md`:

**Authentication Tests**:
- [ ] Login with valid credentials → redirects to task list
- [ ] Login with invalid credentials → shows error
- [ ] Access protected page without auth → redirects to login
- [ ] Logout → clears session and redirects to login

**Task CRUD Tests**:
- [ ] View task list → displays only user's tasks
- [ ] Create task → appears in list immediately
- [ ] Edit task → updates display immediately
- [ ] Delete task with confirmation → removes from list
- [ ] Toggle task status → updates immediately

**Responsive Design Tests**:
- [ ] Test at 320px width (mobile)
- [ ] Test at 768px width (tablet)
- [ ] Test at 1024px width (desktop)
- [ ] Test at 2560px width (large desktop)

**Error Handling Tests**:
- [ ] Network error → shows error message
- [ ] API timeout → shows error message
- [ ] Token expiration → redirects to login
- [ ] Validation error → shows field-specific errors

---

## Common Issues and Solutions

### Issue: "Cannot find module '@/...'"

**Solution**: Ensure `tsconfig.json` has path aliases configured:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

### Issue: "API calls fail with CORS error"

**Solution**: Ensure backend API has CORS configured for `http://localhost:3000`

### Issue: "Authentication not working"

**Solution**:
1. Check `.env.local` has `AUTH_SECRET` configured
2. Verify backend API is running
3. Check browser cookies are enabled
4. Clear browser cookies and retry

### Issue: "Build fails with type errors"

**Solution**:
1. Run `npm run type-check` to see all errors
2. Ensure all API response types match `types/api.ts`
3. Check for missing type imports

---

## Development Best Practices

### 1. Component Organization

- Keep components small and focused (single responsibility)
- Use Server Components by default, Client Components only when needed
- Extract reusable logic into custom hooks

### 2. Type Safety

- Always define TypeScript interfaces for props
- Use API types from `types/api.ts`
- Avoid `any` type - use `unknown` or proper types

### 3. Error Handling

- Always wrap API calls in try-catch
- Display user-friendly error messages
- Log errors for debugging (use console.error)

### 4. Performance

- Use React.memo() for expensive components
- Implement code splitting with dynamic imports
- Optimize images with Next.js Image component

### 5. Accessibility

- Use semantic HTML elements
- Add ARIA labels where needed
- Test keyboard navigation
- Ensure color contrast meets WCAG standards

---

## Useful Resources

### Documentation

- [Next.js 16 Documentation](https://nextjs.org/docs)
- [React 18 Documentation](https://react.dev)
- [Better Auth Documentation](https://better-auth.com/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

### Project Specs

- Feature Specification: `specs/003-frontend-todo-app/spec.md`
- Implementation Plan: `specs/003-frontend-todo-app/plan.md`
- Data Model: `specs/003-frontend-todo-app/data-model.md`
- API Contracts: `specs/003-frontend-todo-app/contracts/api-spec.openapi.yaml`

### Tools

- [React Developer Tools](https://react.dev/learn/react-developer-tools)
- [Next.js DevTools](https://nextjs.org/docs/app/building-your-application/optimizing/instrumentation)
- [Postman](https://www.postman.com/) - API testing

---

## Getting Help

### Debugging Steps

1. **Check browser console** for JavaScript errors
2. **Check Network tab** for failed API requests
3. **Check terminal** for build/server errors
4. **Review error messages** carefully - they usually indicate the problem
5. **Check specifications** to ensure implementation matches requirements

### Where to Look

- **Component errors**: Check component file and props
- **API errors**: Check `lib/api-client.ts` and network tab
- **Auth errors**: Check `lib/auth.ts` and middleware.ts
- **Routing errors**: Check `app/` directory structure
- **Type errors**: Run `npm run type-check` for details

---

## Next Steps

After setup is complete:

1. **Review the specification**: Read `specs/003-frontend-todo-app/spec.md`
2. **Study the data model**: Read `specs/003-frontend-todo-app/data-model.md`
3. **Check API contracts**: Review `specs/003-frontend-todo-app/contracts/api-spec.openapi.yaml`
4. **Start implementing**: Follow tasks in `specs/003-frontend-todo-app/tasks.md` (created by `/sp.tasks`)

---

## Quick Reference

### Environment Variables

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api  # Backend API
AUTH_SECRET=<your-secret>                       # Min 32 chars
AUTH_URL=http://localhost:3000                  # Frontend URL
```

### Port Configuration

- Frontend (Next.js): `http://localhost:3000`
- Backend API: `http://localhost:8000`

### Key Files to Know

- `middleware.ts` - Route protection
- `lib/api-client.ts` - API communication
- `lib/auth.ts` - Authentication setup
- `app/layout.tsx` - Root layout
- `types/api.ts` - API type definitions

---

**Ready to start developing!** 🚀

If you encounter any issues not covered here, check the project specifications or reach out to the team.
