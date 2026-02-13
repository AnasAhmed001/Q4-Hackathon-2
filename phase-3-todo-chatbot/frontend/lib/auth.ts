import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

// Initialize the Better Auth client with JWT plugin
export const auth = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
  fetchOptions: {
    // Configure fetch options for proper cookie handling
    credentials: 'include',
  },
  plugins: [
    jwtClient(), // Enable JWT plugin for token management
  ],
});


// Export auth client methods for use in components
export const { signIn, signOut, useSession } = auth;

/**
 * Get JWT token for API requests to FastAPI backend
 * This token is used to authenticate requests to the FastAPI server
 */
export const getJWTToken = async (): Promise<string | null> => {
  try {
    const baseURL =
      process.env.NEXT_PUBLIC_BETTER_AUTH_URL ||
      process.env.BETTER_AUTH_URL ||
      "http://localhost:3000";

    const isServer = typeof window === "undefined";
    const tokenUrl = isServer ? `${baseURL}/api/auth/token` : "/api/auth/token";

    // Call Better Auth JWT endpoint to get the access token
    const response = await fetch(tokenUrl, {
      credentials: "include",
    });

    if (!response.ok) {
      console.error("Failed to get JWT token:", response.statusText);
      return null;
    }

    const data = await response.json();
    return data.token || null;
  } catch (error) {
    console.error("Error getting JWT token:", error);
    return null;
  }
};

/**
 * Make authenticated API requests with JWT token
 * This is specifically for FastAPI backend requests
 */
export const authenticatedFetch = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  // Get JWT token
  const token = await getJWTToken();

  if (!token) {
    throw new Error("No authentication token available");
  }

  // Attach JWT token to Authorization header
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  });
};

/**
 * Attach JWT token to request options
 * Helper function for manual request construction
 */
export const attachTokenToRequest = async (
  options: RequestInit = {}
): Promise<RequestInit> => {
  const token = await getJWTToken();

  if (!token) {
    throw new Error("No authentication token available");
  }

  return {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  };
};