// Data Model Types

// User Entity
export interface User {
  id: string;
  email: string;
  name?: string;
  createdAt: string;
}

// Task Entity
export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  completed: boolean;
  dueDate?: string;
  userId: string;
  createdAt: string;
  updatedAt: string;
}

export type TaskStatus = 'pending' | 'completed';

// Session Entity
export interface AuthSession {
  user: User;
  token: string;
  expiresAt: string;
}

// UI State Models

// Task List State
export interface TaskListState {
  tasks: Task[];
  filteredTasks: Task[];
  isLoading: boolean;
  error: string | null;
  filter: TaskStatus | 'all';
  searchQuery: string;
}

// Task Form State
export interface TaskFormState {
  mode: 'create' | 'edit';
  task: Partial<Task>;
  errors: Record<string, string>;
  isSubmitting: boolean;
}

// Delete Confirmation State
export interface DeleteConfirmationState {
  isOpen: boolean;
  taskId: string | null;
  isDeleting: boolean;
}