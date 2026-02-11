import { authenticatedFetch } from './auth';
import { Task } from '@/types/models';
import { ChatResponse, ConversationHistoryResponse } from '@/types/api';

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

/**
 * API Client Error
 */
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = "APIError";
  }
}

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

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
    // Use the authenticatedFetch function from auth.ts which handles JWT tokens
    const response = await authenticatedFetch(url, config);

    if (!response.ok) {
      if (response.status === 401) {
        // Token expired or invalid, redirect to login
        window.location.href = '/login';
        throw new APIError('Unauthorized - redirecting to login', 401);
      }

      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.detail || errorData.error?.message || `HTTP error! status: ${response.status}`,
        response.status,
        errorData
      );
    }

    if (response.status === 204) {
      // No content response
      return {} as T;
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
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

/**
 * Task API client
 * Provides methods to interact with the task management endpoints.
 */
export const taskAPI = {
  /**
   * Get all tasks for a user
   */
  async getTasks(userId: string): Promise<Task[]> {
    const res = await apiGet<{ tasks: any[] } | Task[]>(`/api/${userId}/tasks`);
    const tasks = Array.isArray(res) ? res : res?.tasks || [];
    return tasks.map(mapTaskFromApi);
  },

  /**
   * Get a specific task by ID
   */
  async getTask(userId: string, taskId: string): Promise<Task> {
    const res = await apiGet<any>(`/api/${userId}/tasks/${taskId}`);
    return mapTaskFromApi(res);
  },

  /**
   * Create a new task
   */
  async createTask(userId: string, task: {
    title: string;
    description?: string;
    status?: string;
    dueDate?: string;
  }): Promise<Task> {
    const payload = {
      title: task.title,
      description: task.description,
      status: task.status || 'pending',
      due_date: task.dueDate || null,
    };
    const res = await apiPost<any>(`/api/${userId}/tasks`, payload);
    return mapTaskFromApi(res);
  },

  /**
   * Update an existing task
   */
  async updateTask(
    userId: string,
    taskId: string,
    updates: {
      title?: string;
      description?: string;
      status?: string;
      dueDate?: string;
    }
  ): Promise<Task> {
    const payload = {
      title: updates.title,
      description: updates.description,
      status: updates.status,
      due_date: updates.dueDate,
    };
    const res = await apiPut<any>(`/api/${userId}/tasks/${taskId}`, payload);
    return mapTaskFromApi(res);
  },

  /**
   * Delete a task
   */
  async deleteTask(userId: string, taskId: string): Promise<void> {
    return apiDelete<void>(`/api/${userId}/tasks/${taskId}`);
  },
};

// Helper to normalize API task shape to frontend Task type
function mapTaskFromApi(apiTask: any): Task {
  return {
    id: apiTask.id,
    title: apiTask.title,
    description: apiTask.description || '',
    status: apiTask.status || 'pending',
    completed: (apiTask.status || 'pending') === 'completed',
    dueDate: apiTask.due_date || apiTask.dueDate || null,
    userId: apiTask.user_id || apiTask.userId,
    createdAt: apiTask.created_at || apiTask.createdAt,
    updatedAt: apiTask.updated_at || apiTask.updatedAt,
  } as Task;
}

/**
 * User API client
 * Provides methods to interact with user-related endpoints.
 */
export const userAPI = {
  /**
   * Get current user profile
   */
  async getProfile(userId: string) {
    return apiGet(`/api/${userId}/profile`);
  },
};

/**
 * Chat API client
 * Provides methods to interact with the chatbot endpoints.
 */
export const chatAPI = {
  /**
   * Send a message to the chatbot
   */
  async sendMessage(userId: string, message: string, conversationId?: string): Promise<ChatResponse> {
    return apiPost<ChatResponse>(`/api/${userId}/chat`, {
      message,
      conversation_id: conversationId,
    });
  },

  /**
   * Get list of user's conversations
   */
  async getConversations(userId: string, params?: { skip?: number; limit?: number }) {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());

    const queryString = queryParams.toString();
    return apiGet(`/api/${userId}/conversations${queryString ? '?' + queryString : ''}`);
  },

  /**
   * Get conversation history
   */
  async getConversationHistory(userId: string, conversationId: string, params?: { skip?: number; limit?: number }): Promise<ConversationHistoryResponse> {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());

    const queryString = queryParams.toString();
    return apiGet<ConversationHistoryResponse>(`/api/${userId}/conversations/${conversationId}${queryString ? '?' + queryString : ''}`);
  },
};