'use client';

import { useState, useEffect, useOptimistic, startTransition } from 'react';
import { Task } from '@/types/models';
import { getTasksAction, createTaskAction, updateTaskAction, deleteTaskAction } from '@/app/(protected)/tasks/actions';
import { TaskList } from '@/components/tasks/TaskList';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Plus } from 'lucide-react';
import { TaskForm } from '@/components/tasks/TaskForm';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';


interface TasksClientProps {
  initialTasks: Task[];
  userId: string;
}

type OptimisticAction =
  | { type: 'reset'; tasks: Task[] }
  | { type: 'add'; task: Task }
  | { type: 'update'; task: Task }
  | { type: 'delete'; id: string }
  | { type: 'toggle'; id: string; completed: boolean; status?: Task['status'] };

function optimisticReducer(state: Task[], action: OptimisticAction): Task[] {
  switch (action.type) {
    case 'reset':
      return action.tasks;
    case 'add':
      return [action.task, ...state];
    case 'update':
      return state.map((task) => (task.id === action.task.id ? { ...task, ...action.task } : task));
    case 'delete':
      return state.filter((task) => task.id !== action.id);
    case 'toggle':
      return state.map((task) =>
        task.id === action.id
            ? { ...task, completed: action.completed, status: action.status ?? (action.completed ? 'completed' : 'pending') }
          : task
      );
    default:
      return state;
  }
}

const useOptimisticTyped = useOptimistic as unknown as <State, Action>(
  initialState: State,
  updateFn: (state: State, action: Action) => State
) => [State, (action: Action) => void];

export function TasksClient({ initialTasks, userId }: TasksClientProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);
  const [editError, setEditError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [updating, setUpdating] = useState(false);



  const [optimisticTasks, addOptimisticTask] = useOptimisticTyped(tasks, optimisticReducer);
  const [statusFilter, setStatusFilter] = useState<Task['status'] | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    startTransition(() => {
      addOptimisticTask({ type: 'reset', tasks });
    });
  }, [tasks, addOptimisticTask]);

  useEffect(() => {
    if (!userId) return;
    refreshTasks();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  // Refresh tasks when the chatbot modifies them (with optimistic updates)
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail as {
        ops?: Array<{ tool: string; args: Record<string, any>; result: Record<string, any> }>;
        userId?: string;
      } | undefined;

      if (!detail?.ops?.length) {
        refreshTasks(false);
        return;
      }

      // Apply optimistic updates immediately
      setTasks((prev) => {
        let next = [...prev];
        for (const op of detail.ops!) {
          if (op.tool === 'add_task' && op.result.task_id) {
            const now = new Date().toISOString();
            next = [
              {
                id: op.result.task_id,
                title: op.args.title || op.result.title || 'New task',
                description: op.args.description || '',
                status: (op.args.status as Task['status']) || 'pending',
                completed: op.args.status === 'completed',
                dueDate: op.args.due_date,
                userId: op.args.user_id || userId,
                createdAt: now,
                updatedAt: now,
              },
              ...next,
            ];
          } else if (op.tool === 'complete_task' && op.result.task_id) {
            next = next.map((t) =>
              t.id === op.result.task_id
                ? { ...t, status: 'completed' as Task['status'], completed: true, updatedAt: new Date().toISOString() }
                : t,
            );
          } else if (op.tool === 'update_task' && op.result.task_id) {
            next = next.map((t) =>
              t.id === op.result.task_id
                ? {
                    ...t,
                    ...(op.args.title && { title: op.args.title }),
                    ...(op.args.description !== undefined && { description: op.args.description }),
                    ...(op.args.status && { status: op.args.status as Task['status'], completed: op.args.status === 'completed' }),
                    ...(op.args.due_date && { dueDate: op.args.due_date }),
                    updatedAt: new Date().toISOString(),
                  }
                : t,
            );
          } else if (op.tool === 'delete_task' && op.result.task_id) {
            next = next.filter((t) => t.id !== op.result.task_id);
          }
        }
        return next;
      });

      // Background sync with actual DB state after a short delay
      setTimeout(() => refreshTasks(false), 1500);
    };
    window.addEventListener('tasks-updated', handler);
    return () => window.removeEventListener('tasks-updated', handler);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);



  const refreshTasks = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      const tasks = await getTasksAction(userId);
      setTasks(tasks);
      setError(null);
      startTransition(() => {
        addOptimisticTask({ type: 'reset', tasks });
      });
    } catch (err) {
      setError('Failed to load tasks. Please try again.');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
      setInitialLoading(false);
    }
  };

  const handleCreateTask = () => {
    setCreateError(null);
    setCreateDialogOpen(true);
  };

  const handleSubmitCreate = async (taskData: Partial<Task>) => {
    if (!userId) {
      setCreateError('You must be signed in to create a task.');
      return;
    }

    setCreating(true);
    setCreateError(null);
    setCreateDialogOpen(false);

    const tempId = `temp-${typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : Date.now()}`;
    const optimisticTask: Task = {
      id: tempId,
      title: taskData.title || 'Untitled',
      description: taskData.description || '',
      status: (taskData.status as Task['status']) || 'pending',
      completed: (taskData.status || 'pending') === 'completed',
      dueDate: taskData.dueDate || undefined,
      userId,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    const optimisticNext = [optimisticTask, ...tasks];
    setTasks(optimisticNext);
    startTransition(() => {
      addOptimisticTask({ type: 'reset', tasks: optimisticNext });
    });

    try {
      const newTask = await createTaskAction(userId, {
        title: taskData.title || '',
        description: taskData.description,
        status: taskData.status,
        dueDate: taskData.dueDate || undefined,
      });

      const filtered = optimisticNext.filter((t) => t.id !== tempId);
      const nextTasks = [newTask, ...filtered];
      setTasks(nextTasks);
      startTransition(() => {
        addOptimisticTask({ type: 'reset', tasks: nextTasks });
      });
      setCreateDialogOpen(false);
    } catch (err) {
      console.error(err);
      setCreateError('Failed to create task. Please try again.');
      setTasks(tasks);
      startTransition(() => {
        addOptimisticTask({ type: 'reset', tasks });
      });
    } finally {
      setCreating(false);
    }
  };

  const handleCancelCreate = () => {
    setCreateDialogOpen(false);
    setCreateError(null);
  };

  const handleOpenEdit = (task: Task) => {
    setEditingTask(task);
    setEditError(null);
    setEditDialogOpen(true);
  };

  const handleSubmitEdit = async (taskData: Partial<Task>) => {
    if (!userId || !editingTask) return;

    setUpdating(true);
    setEditError(null);
    setEditDialogOpen(false);

    const previous = tasks;
    const updatedDraft: Task = {
      ...editingTask,
      ...taskData,
      completed: (taskData.status || editingTask.status) === 'completed',
    };
    const optimisticNext = tasks.map((t) => (t.id === editingTask.id ? updatedDraft : t));
    setTasks(optimisticNext);
    startTransition(() => {
      addOptimisticTask({ type: 'reset', tasks: optimisticNext });
    });

    try {
      const updated = await updateTaskAction(userId, editingTask.id, {
        title: taskData.title,
        description: taskData.description,
        status: taskData.status as Task['status'] | undefined,
        dueDate: taskData.dueDate || undefined,
      });

      const nextTasks = optimisticNext.map((t) => (t.id === updated.id ? updated : t));
      setTasks(nextTasks);
      startTransition(() => {
        addOptimisticTask({ type: 'reset', tasks: nextTasks });
      });
      setEditingTask(null);
    } catch (err) {
      console.error(err);
      setEditError('Failed to update task. Please try again.');
      setTasks(previous);
      startTransition(() => {
        addOptimisticTask({ type: 'reset', tasks: previous });
      });
    } finally {
      setUpdating(false);
    }
  };

  const handleCancelEdit = () => {
    setEditDialogOpen(false);
    setEditingTask(null);
    setEditError(null);
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!userId) return;

    const previous = tasks;
    const optimisticNext = tasks.filter((t) => t.id !== taskId);
    setTasks(optimisticNext);
    startTransition(() => {
      addOptimisticTask({ type: 'reset', tasks: optimisticNext });
    });

    try {
      await deleteTaskAction(userId, taskId);
      setTasks(optimisticNext);
      startTransition(() => {
        addOptimisticTask({ type: 'reset', tasks: optimisticNext });
      });
    } catch (err) {
      setError('Failed to delete task');
      setTasks(previous);
      startTransition(() => {
        addOptimisticTask({ type: 'reset', tasks: previous });
      });
      console.error(err);
    }
  };

  const handleToggleComplete = async (taskId: string, completed: boolean) => {
    if (!userId) return;

    const task = tasks.find((t) => t.id === taskId);
    if (!task) return;

    const previous = tasks;
    const optimisticNext = tasks.map((t) =>
      t.id === taskId
        ? { ...t, status: (completed ? 'completed' : 'pending') as Task['status'], completed }
        : t
    );

    // Update local state immediately to avoid UI flicker, then keep optimistic list in sync.
    setTasks(optimisticNext);
    startTransition(() => {
      addOptimisticTask({ type: 'reset', tasks: optimisticNext });
    });

    try {
      const updated = await updateTaskAction(userId, taskId, {
        status: (completed ? 'completed' : 'pending') as Task['status'],
      });
      const nextTasks = optimisticNext.map((t) => (t.id === taskId ? updated : t));
      setTasks(nextTasks);
      startTransition(() => {
        addOptimisticTask({ type: 'reset', tasks: nextTasks });
      });
    } catch (err) {
      setError('Failed to update task');
      setTasks(previous);
      startTransition(() => {
        addOptimisticTask({ type: 'reset', tasks: previous });
      });
      console.error(err);
    }
  };

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error! </strong>
        <span className="block sm:inline">{error}</span>
        <button
          onClick={() => refreshTasks()}
          className="mt-2 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6 px-4 py-8 text-foreground bg-background">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold text-foreground">Tasks</h1>
          <p className="text-sm text-muted-foreground">Stay on top of what needs doing.</p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <Button onClick={handleCreateTask}>
            <Plus className="h-4 w-4" aria-hidden="true" />
            New Task
          </Button>
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-card/80 p-4 shadow-sm backdrop-blur-sm sm:p-6">
        {initialLoading && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Skeleton className="h-8 w-32 bg-muted" />
              <Skeleton className="h-10 w-28 bg-muted" />
            </div>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="space-y-2 rounded-lg border border-border/60 bg-card p-4">
                  <Skeleton className="h-5 w-2/3 bg-muted" />
                  <Skeleton className="h-4 w-full bg-muted" />
                  <Skeleton className="h-4 w-1/3 bg-muted" />
                </div>
              ))}
            </div>
          </div>
        )}

        {!initialLoading && optimisticTasks.length === 0 && (
          <div className="py-12 text-center">
            <p className="text-muted-foreground text-lg">No tasks yet. Create your first task!</p>
          </div>
        )}

        {!initialLoading && optimisticTasks.length > 0 && (
          <TaskList
            tasks={optimisticTasks}
            onToggleComplete={handleToggleComplete}
            onTaskDelete={handleDeleteTask}
            onEditTask={handleOpenEdit}
            statusFilter={statusFilter}
            searchQuery={searchQuery}
            onStatusChange={setStatusFilter}
            onSearchChange={setSearchQuery}
          />
        )}
      </div>

      <Dialog
        open={createDialogOpen}
        onOpenChange={(open) => {
          setCreateDialogOpen(open);
          if (!open) setCreateError(null);
        }}
      >
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Create Task</DialogTitle>
            <DialogDescription>Fill out the details for your new task.</DialogDescription>
          </DialogHeader>
          {createError && (
            <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {createError}
            </div>
          )}
          <TaskForm
            onSubmit={handleSubmitCreate}
            onCancel={handleCancelCreate}
            mode="create"
            isSubmitting={creating}
            submitLabel="Create Task"
          />
        </DialogContent>
      </Dialog>

      <Dialog
        open={editDialogOpen}
        onOpenChange={(open) => {
          setEditDialogOpen(open);
          if (!open) {
            setEditingTask(null);
            setEditError(null);
          }
        }}
      >
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Edit Task</DialogTitle>
            <DialogDescription>Update the details for this task.</DialogDescription>
          </DialogHeader>
          {editError && (
            <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {editError}
            </div>
          )}
          {editingTask && (
            <TaskForm
              task={editingTask}
              onSubmit={handleSubmitEdit}
              onCancel={handleCancelEdit}
              mode="edit"
              isSubmitting={updating}
              submitLabel="Update Task"
            />
          )}
        </DialogContent>
      </Dialog>


    </div>
  );
}
