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

// Chat
export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatToolCall {
  name: string;
  arguments?: Record<string, any> | null;
}

export interface ChatToolResponse {
  name: string;
  output: any;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls?: ChatToolCall[];
  tool_responses?: ChatToolResponse[];
}

export interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface ConversationHistoryResponse {
  messages: ConversationMessage[];
  total_count: number;
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