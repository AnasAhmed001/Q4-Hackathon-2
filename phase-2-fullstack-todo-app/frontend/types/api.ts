// API Request/Response Types

// Authentication
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  token: string;
  expiresAt: string;
}

export interface LogoutResponse {
  success: boolean;
  message: string;
}

// User
export interface User {
  id: string;
  email: string;
  name?: string;
  createdAt: string;
}

// Task
export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  dueDate?: string;
  userId: string;
  createdAt: string;
  updatedAt: string;
}

export type TaskStatus = 'pending' | 'completed';

// API Requests
export interface GetTasksParams {
  status?: TaskStatus;
  search?: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  status?: TaskStatus;
  dueDate?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
  dueDate?: string;
}

// API Responses
export interface GetTasksResponse {
  tasks: Task[];
  total: number;
}

export interface CreateTaskResponse {
  task: Task;
  message: string;
}

export interface UpdateTaskResponse {
  task: Task;
  message: string;
}

export interface DeleteTaskResponse {
  success: boolean;
  message: string;
}

// Error Response
export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, string>;
  };
  statusCode: number;
}