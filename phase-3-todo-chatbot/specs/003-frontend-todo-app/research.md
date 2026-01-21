# Research: Frontend Todo Application

**Feature**: 003-frontend-todo-app
**Date**: 2026-01-13
**Phase**: Phase 0 - Technology Research and Decision Making

## Overview

This document consolidates all research findings and technology decisions for implementing the Frontend Todo Application. All decisions are aligned with the user-provided technical requirements and project constitution principles.

---

## Technology Stack Decisions

### Decision 1: Next.js 16 with App Router

**Decision**: Use Next.js 16 with App Router as the frontend framework

**Rationale**:
- Next.js 16 provides modern React 18+ features with Server Components support
- App Router offers file-system based routing with improved performance
- Built-in support for server and client components enables optimal rendering strategies
- Excellent TypeScript support and developer experience
- Large ecosystem and strong community support

**Alternatives Considered**:
- **Vite + React Router**: More lightweight but requires more configuration and lacks SSR capabilities
- **Create React App**: Deprecated and doesn't support modern React features
- **Remix**: Strong alternative but less ecosystem maturity than Next.js

**Implementation Notes**:
- Use App Router (`app/` directory) for all routes
- Leverage Server Components for static content and data fetching
- Use Client Components only where interactivity is required
- Follow Next.js 16 best practices for code splitting and lazy loading

---

### Decision 2: Better Auth for Authentication

**Decision**: Use Better Auth library for session management and authentication

**Rationale**:
- Purpose-built for Next.js applications with excellent App Router integration
- Provides secure session handling out of the box
- Supports JWT token extraction and management
- Simplifies authentication flow implementation
- Type-safe API that integrates well with TypeScript

**Alternatives Considered**:
- **NextAuth.js (Auth.js)**: Popular but more complex for simple use cases
- **Custom JWT implementation**: More control but higher risk of security vulnerabilities
- **Clerk/Auth0**: Managed services with vendor lock-in and additional costs

**Implementation Notes**:
- Configure Better Auth in `lib/auth.ts` or similar
- Extract JWT tokens from Better Auth session for API requests
- Implement middleware for route protection
- Store session data securely (httpOnly cookies)

---

### Decision 3: Centralized API Client Architecture

**Decision**: Implement a centralized fetch wrapper for all backend API communication

**Rationale**:
- Single point of configuration for API base URL and headers
- Automatic Authorization header injection from Better Auth session
- Consistent error handling across all API calls
- Simplified testing and mocking
- Easier to implement retry logic and request/response interceptors

**Alternatives Considered**:
- **Direct fetch calls**: Simple but leads to code duplication and inconsistent error handling
- **Axios**: Additional dependency when native fetch is sufficient with a wrapper
- **TanStack Query (React Query)**: Powerful but adds complexity for simple CRUD operations

**Implementation Notes**:
- Create `lib/api-client.ts` with wrapper function
- Extract JWT from Better Auth session on each request
- Handle 401 responses by redirecting to login
- Handle 403, 404, 500 errors with appropriate user feedback
- Support request/response type safety with TypeScript generics

---

### Decision 4: Optimistic UI Updates with State Synchronization

**Decision**: Implement optimistic UI updates that sync with API responses

**Rationale**:
- Provides immediate user feedback for better UX
- Reduces perceived latency from network requests
- Automatically reverts on API failures
- Aligns with SC-002 (task creation under 5 seconds) and SC-004 (status update under 3 seconds)

**Alternatives Considered**:
- **Wait for API response**: Simple but poor UX with network latency
- **Local state only**: Fast but loses data on refresh and has sync issues
- **TanStack Query mutations**: Excellent but adds library dependency

**Implementation Notes**:
- Update local state immediately on user action
- Send API request in background
- On success: Keep optimistic update
- On failure: Revert to previous state and show error message
- Use React state or lightweight state management (Zustand) if needed

---

### Decision 5: Responsive Design with CSS Modules and Tailwind CSS

**Decision**: Use Tailwind CSS for responsive styling

**Rationale**:
- Utility-first approach enables rapid UI development
- Built-in responsive design utilities (sm, md, lg, xl breakpoints)
- Aligns with SC-003 requirement (320px to 2560px width support)
- Excellent Next.js integration
- Small bundle size with tree-shaking

**Alternatives Considered**:
- **CSS Modules**: Good for scoping but more verbose for responsive design
- **Styled Components**: Runtime overhead and SSR complexity in Next.js 16
- **Plain CSS**: Most control but slower development and harder maintenance

**Implementation Notes**:
- Configure Tailwind in `tailwind.config.js`
- Use responsive breakpoints: `sm:`, `md:`, `lg:`, `xl:`, `2xl:`
- Implement mobile-first design approach
- Test on minimum width (320px) and maximum width (2560px)

---

## Architecture Patterns

### Pattern 1: Server and Client Component Separation

**Decision**: Use Server Components for layouts and static content, Client Components for interactive UI

**Rationale**:
- Server Components reduce JavaScript bundle size
- Better initial page load performance
- Client Components only where needed (forms, buttons, interactive elements)
- Aligns with Next.js 16 App Router best practices

**Implementation Strategy**:
- Mark interactive components with `"use client"` directive
- Keep task list rendering on server side when possible
- Use Client Components for:
  - Task creation form
  - Task edit form
  - Delete confirmation dialog
  - Search and filter controls
  - Status toggle buttons

---

### Pattern 2: Protected Route Middleware

**Decision**: Implement Next.js middleware for authentication protection

**Rationale**:
- Centralized authentication checks
- Prevents unauthorized access before page render
- Aligns with FR-004 (redirect unauthenticated users)
- Efficient - runs on edge before rendering

**Implementation Strategy**:
- Create `middleware.ts` in project root
- Check Better Auth session validity
- Redirect to `/login` if unauthenticated
- Allow public routes (login, signup)
- Protect all `/tasks/*` routes

---

### Pattern 3: Error Boundary and Loading States

**Decision**: Implement React Error Boundaries and Suspense for error and loading states

**Rationale**:
- Aligns with FR-013 (display error messages) and FR-017 (loading states)
- Prevents application crashes from unhandled errors
- Better user experience with loading indicators
- Built-in Next.js support with `error.tsx` and `loading.tsx`

**Implementation Strategy**:
- Create `error.tsx` files for route-level error boundaries
- Create `loading.tsx` files for route-level loading states
- Use Suspense for component-level loading
- Display user-friendly error messages
- Provide recovery actions (retry, go home)

---

## API Integration Patterns

### Pattern 1: Typed API Responses

**Decision**: Define TypeScript interfaces for all API request/response types

**Rationale**:
- Type safety prevents runtime errors
- Better IDE autocomplete and developer experience
- Self-documenting API contracts
- Easier refactoring and maintenance

**Implementation Strategy**:
- Create `types/api.ts` with interface definitions
- Define types for User, Task, and API responses
- Use generic types in API client for type inference
- Validate API responses match expected types

---

### Pattern 2: Token Refresh and Session Handling

**Decision**: Handle token expiration gracefully with automatic refresh or re-login

**Rationale**:
- Aligns with FR-016 (handle token expiration)
- Better user experience than sudden authentication loss
- Security best practice for session management

**Implementation Strategy**:
- Detect 401 responses in API client
- Attempt token refresh if Better Auth supports it
- If refresh fails, clear session and redirect to login
- Show user-friendly message explaining session expiration
- Preserve user's current page for post-login redirect

---

## Performance Considerations

### Optimization 1: Code Splitting and Lazy Loading

**Decision**: Use Next.js automatic code splitting and lazy loading for non-critical components

**Rationale**:
- Reduces initial bundle size
- Faster page loads
- Aligns with SC-002 and SC-004 (fast task operations)

**Implementation Strategy**:
- Let Next.js handle automatic page-level code splitting
- Use `React.lazy()` for modals and dialogs
- Load large components (task editor) on demand
- Minimize third-party dependencies

---

### Optimization 2: Client-Side Caching Strategy

**Decision**: Implement simple client-side caching for task list data

**Rationale**:
- Reduces API calls for frequently accessed data
- Improves perceived performance
- Aligns with SC-010 (functional with 500 tasks)

**Implementation Strategy**:
- Cache task list in React state or Zustand store
- Invalidate cache after mutations (create, update, delete)
- Consider short-lived cache (5-10 seconds) for refresh button
- No offline support (per "Not building" constraint)

---

## Security Implementation

### Security 1: Token Storage and Transmission

**Decision**: Store JWT in httpOnly cookies via Better Auth, never in localStorage

**Rationale**:
- Aligns with FR-015 (no sensitive data exposure)
- Prevents XSS attacks from stealing tokens
- Better Auth handles secure cookie management
- httpOnly cookies not accessible to JavaScript

**Implementation Strategy**:
- Let Better Auth manage cookie storage
- Extract token only when needed for API requests
- Never log tokens to console
- Use HTTPS in production

---

### Security 2: Input Validation and Sanitization

**Decision**: Validate all user inputs on client side before API submission

**Rationale**:
- Aligns with FR-007 (validate required fields)
- Prevents invalid API requests
- Better user experience with immediate feedback
- Defense in depth (backend also validates)

**Implementation Strategy**:
- Validate required fields (task title)
- Limit input lengths to reasonable values
- Sanitize HTML if description supports rich text
- Show validation errors inline with form fields
- Disable submit button until form is valid

---

## Testing Strategy

### Testing Approach: Manual Testing with Test Checklist

**Decision**: Focus on manual testing with comprehensive test checklist based on acceptance criteria

**Rationale**:
- Hackathon timeline prioritizes working features over test automation
- Spec provides detailed acceptance scenarios for manual verification
- Constitution requires testability, not necessarily automated tests
- Manual testing sufficient for demo readiness

**Implementation Strategy**:
- Create test checklist from spec acceptance scenarios
- Test each user story independently (P1, P2, P3)
- Verify edge cases manually
- Test on multiple screen sizes (320px, 768px, 1024px, 2560px)
- Test authentication flows (login, logout, token expiration)
- Verify all success criteria before demo

---

## Deployment Considerations

### Deployment: Vercel Platform

**Decision**: Deploy to Vercel for optimal Next.js 16 performance

**Rationale**:
- Built by Next.js creators with best integration
- Automatic deployments from Git
- Edge network for fast global access
- Free tier sufficient for hackathon demo
- Zero configuration required

**Implementation Strategy**:
- Connect GitHub repository to Vercel
- Configure environment variables (API URL, auth secrets)
- Enable preview deployments for testing
- Use production deployment for demo

---

## Unknowns and Clarifications Resolved

### Q1: Backend API Base URL

**Resolved**: Will be configured via environment variable `NEXT_PUBLIC_API_URL`

**Rationale**: Allows different URLs for development, staging, and production without code changes

---

### Q2: Task Status Values

**Resolved**: Based on spec entities, status values are "pending" and "completed"

**Rationale**: Spec defines status as "pending/completed" in Key Entities section

---

### Q3: Authentication Flow Details

**Resolved**: Better Auth will handle session creation, JWT extraction performed in API client

**Rationale**: Better Auth provides complete authentication flow, we only need to integrate with existing backend API

---

### Q4: Error Message Display Strategy

**Resolved**: Use toast notifications for transient errors, inline errors for form validation

**Rationale**:
- Toast notifications for API errors (FR-013) provide non-blocking feedback
- Inline validation errors (FR-007) keep context close to input fields
- Aligns with SC-006 (errors within 2 seconds)

---

## Summary

All technology decisions are finalized and ready for Phase 1 (Design & Contracts). The research establishes:

✅ **Frontend Framework**: Next.js 16 with App Router
✅ **Authentication**: Better Auth with JWT extraction
✅ **API Client**: Centralized fetch wrapper with automatic auth injection
✅ **Styling**: Tailwind CSS for responsive design
✅ **State Management**: React state with optimistic updates
✅ **Security**: httpOnly cookies, input validation, no sensitive data exposure
✅ **Deployment**: Vercel platform
✅ **Testing**: Manual testing with comprehensive checklist

No blocking unknowns remain. Ready to proceed to Phase 1: Data Model and API Contracts.
