import { auth, getAuthToken, authenticatedFetch, attachTokenToRequest } from './auth';

// Utility to protect routes on the client side
export const requireAuth = async (redirectPath: string = '/login'): Promise<boolean> => {
  try {
    const session = await auth.getSession();
    if (!session) {
      // Redirect to login page
      window.location.href = redirectPath;
      return false;
    }
    return true;
  } catch (error) {
    console.error('Auth check failed:', error);
    window.location.href = redirectPath;
    return false;
  }
};

// Utility to get user info from session
export const getUserInfo = async () => {
  try {
    const session = await auth.getSession();
    return session?.user || null;
  } catch (error) {
    console.error('Error getting user info:', error);
    return null;
  }
};

// Utility to check if user is authenticated
export const isAuthenticated = async (): Promise<boolean> => {
  try {
    const session = await auth.getSession();
    return !!session && !!session.user;
  } catch (error) {
    console.error('Error checking auth status:', error);
    return false;
  }
};

// Enhanced fetch wrapper with error handling that uses Better Auth's httpOnly cookie mechanism
export const apiRequest = async (
  endpoint: string,
  options: RequestInit = {},
  baseUrl?: string
) => {
  const url = baseUrl ? `${baseUrl}${endpoint}` : endpoint;

  try {
    // Use the authenticatedFetch which handles httpOnly cookies properly
    const response = await authenticatedFetch(url, {
      ...options,
      credentials: 'include', // Ensure cookies are sent with the request
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Handle unauthorized - maybe redirect to login
        window.location.href = '/login';
        throw new Error('Unauthorized: Please log in again');
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

// Export everything as a unified auth utilities object
export const authUtils = {
  requireAuth,
  getUserInfo,
  isAuthenticated,
  apiRequest,
  getAuthToken,
  authenticatedFetch,
  attachTokenToRequest,
  ...auth,
};

export type { Session } from 'better-auth';