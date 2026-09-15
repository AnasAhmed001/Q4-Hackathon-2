import { auth } from "@/lib/auth-server";
import { toNextJsHandler } from "better-auth/next-js";

/**
 * Better Auth API Route Handler
 * 
 * This catch-all route handles all authentication endpoints:
 * - POST /api/auth/sign-up/email - Register new user
 * - POST /api/auth/sign-in/email - Sign in with email/password
 * - POST /api/auth/sign-out - Sign out current user
 * - GET /api/auth/session - Get current session
 * - GET /api/auth/get-jwt - Get JWT token for API calls
 * 
 * The toNextJsHandler automatically maps Better Auth methods
 * to Next.js Request/Response handlers.
 */
export const { GET, POST } = toNextJsHandler(auth);
