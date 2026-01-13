import { authenticatedFetch } from './auth';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

interface ApiResponse<T> {
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, string>;
  };
  statusCode: number;
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const createApiRequest = async <T>(
  endpoint: string,
  options: {
    method?: HttpMethod;
    data?: any;
    headers?: Record<string, string>;
  } = {}
): Promise<T> => {
  const { method = 'GET', data, headers = {} } = options;

  const url = `${BASE_URL}${endpoint}`;

  const config: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  };

  if (data) {
    config.body = JSON.stringify(data);
  }

  try {
    // Use the authenticatedFetch function from auth.ts which handles credentials
    const response = await authenticatedFetch(url, config);

    if (!response.ok) {
      if (response.status === 401) {
        // Token expired or invalid, redirect to login
        window.location.href = '/login';
        throw new Error('Unauthorized - redirecting to login');
      }

      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error?.message || `HTTP error! status: ${response.status}`);
    }

    if (response.status === 204) {
      // No content response
      return {} as T;
    }

    return await response.json();
  } catch (error) {
    console.error(`API request failed: ${method} ${url}`, error);
    throw error;
  }
};

// Convenience methods
export const apiGet = async <T>(endpoint: string, headers?: Record<string, string>): Promise<T> => {
  return createApiRequest<T>(endpoint, { method: 'GET', headers });
};

export const apiPost = async <T>(endpoint: string, data?: any, headers?: Record<string, string>): Promise<T> => {
  return createApiRequest<T>(endpoint, { method: 'POST', data, headers });
};

export const apiPut = async <T>(endpoint: string, data?: any, headers?: Record<string, string>): Promise<T> => {
  return createApiRequest<T>(endpoint, { method: 'PUT', data, headers });
};

export const apiDelete = async <T>(endpoint: string, headers?: Record<string, string>): Promise<T> => {
  return createApiRequest<T>(endpoint, { method: 'DELETE', headers });
};

// Combined API client object
export const apiClient = {
  get: apiGet,
  post: apiPost,
  put: apiPut,
  delete: apiDelete,
};