'use client';

import { useState, useEffect } from 'react';
import { Task } from '@/types/models';
import { apiClient } from '@/lib/api-client';
import { TaskList } from '@/components/tasks/TaskList';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const router = useRouter();

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get<any>('/tasks');
      setTasks(response.tasks || []);
      setError(null);
    } catch (err) {
      setError('Failed to load tasks. Please try again.');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = () => {
    router.push('/tasks/new');
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error! </strong>
        <span className="block sm:inline">{error}</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">My Tasks</h1>
        <Button onClick={handleCreateTask}>
          Create Task
        </Button>
      </div>

      <TaskList
        tasks={tasks}
        onTaskUpdate={fetchTasks}
        onTaskDelete={fetchTasks}
      />

      {tasks.length === 0 && (
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900">No tasks yet</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating a new task.
          </p>
          <div className="mt-6">
            <Button onClick={handleCreateTask}>
              Create your first task
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}