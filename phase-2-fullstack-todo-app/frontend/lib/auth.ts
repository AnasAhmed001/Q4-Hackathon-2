import { createAuthClient } from "better-auth/react";

// Initialize the Better Auth client
export const auth = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:8000",
  fetchOptions: {
    // Configure fetch options for proper cookie handling
    credentials: 'include',
  },
});

// Export auth client methods for use in components
export const { signIn, signOut, useSession } = auth;

// Function to get session and extract token for API requests
export const getAuthToken = async (): Promise<string | null> => {
  try {
    const session = await auth.getSession();
    // Better Auth typically handles authentication via httpOnly cookies,
    // but if you need to extract a JWT token for API requests to external services:
    return session?.accessToken || null;
  } catch (error) {
    console.error("Error getting auth token:", error);
    return null;
  }
};

// Function to make authenticated API requests with proper cookie handling
export const authenticatedFetch = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  // For Better Auth, authentication is typically handled via httpOnly cookies
  // The cookies will be automatically included in requests to the same origin
  // due to credentials: 'include' configuration

  return fetch(url, {
    ...options,
    credentials: 'include', // This ensures httpOnly cookies are sent with requests
  });
};

// Function to attach auth context to API requests
export const attachTokenToRequest = async (
  options: RequestInit = {}
): Promise<RequestInit> => {
  // For Better Auth, we primarily rely on httpOnly cookies for authentication
  // which are automatically handled by the browser when credentials: 'include'
  return {
    ...options,
    credentials: 'include',
  };
};