# Authentication Setup with Better Auth

This project uses Better Auth for authentication and session management. Here's how to set it up and use it:

## Configuration

1. Copy the `.env.example` to `.env.local` and set your configuration:
   ```bash
   NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

## Key Features Implemented

### 1. Session Management
- HttpOnly cookies for secure session storage
- Automatic session handling via Better Auth
- Client-side session state management with React hooks

### 2. Authentication Components
- Login page (`/login`)
- Signup page (`/signup`)
- Protected dashboard (`/dashboard`)

### 3. API Integration
- Automatic JWT token attachment to API requests
- HttpOnly cookie handling for authentication
- Protected route middleware

### 4. Security Features
- CSRF protection
- Secure cookie attributes (httpOnly, secure, sameSite)
- Session validation and management

## Usage

### In Components
```typescript
import { useSession, signIn, signOut } from '@/lib/auth';

// Check session state
const { data: session, isPending } = useSession();

// Sign in
await signIn.email({ email, password });

// Sign out
await signOut();
```

### Making Authenticated API Requests
```typescript
import { authenticatedFetch } from '@/lib/auth';

// This automatically includes the session cookie
const response = await authenticatedFetch('/api/user-data');
```

### Protected Routes
The middleware in `middleware.ts` protects routes:
- `/dashboard/*` - requires authentication
- `/login` and `/signup` - redirects authenticated users away

## Files Created

- `lib/auth.ts` - Main auth client configuration
- `lib/auth-utils.ts` - Helper functions for auth operations
- `components/auth-wrapper.tsx` - Auth context provider
- `app/login/page.tsx` - Login page
- `app/signup/page.tsx` - Signup page
- `app/dashboard/page.tsx` - Protected dashboard
- `middleware.ts` - Route protection middleware