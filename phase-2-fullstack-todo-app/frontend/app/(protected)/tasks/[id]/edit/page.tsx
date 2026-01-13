'use client';

import { useState, useEffect } from 'react';
import { Task } from '@/types/models';
import { apiClient } from '@/lib/api-client';
import { TaskForm } from '@/components/tasks/TaskForm';
import { useRouter, useParams } from 'next/navigation';

export default function EditTaskPage() {
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const router = useRouter();
  const params = useParams();

  useEffect(() => {
    fetchTask();
  }, []);

  const fetchTask = async () => {
    try {
      setLoading(true);
      const fetchedTask = await apiClient.get<Task>(`/tasks/${params.id}`);
      setTask(fetchedTask);
      setError(null);
    } catch (err) {
      setError('Failed to load task. Please try again.');
      console.error('Error fetching task:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (taskData: Partial<Task>) => {
    setLoading(true);
    setError(null);

    try {
      await apiClient.put(`/tasks/${params.id}`, taskData);
      // Redirect to tasks list after successful update
      router.push('/tasks');
      router.refresh(); // Refresh to update the UI
    } catch (err) {
      setError('Failed to update task. Please try again.');
      console.error('Error updating task:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    router.push('/tasks');
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

  if (!task) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">Task not found</h3>
        <p className="mt-1 text-sm text-gray-500">
          The task you are looking for may have been deleted.
        </p>
        <div className="mt-6">
          <button
            onClick={() => router.push('/tasks')}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Go to Tasks
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Edit Task</h1>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">Error! </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      <div className="bg-white p-6 rounded-lg shadow-md">
        <TaskForm
          task={task}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          mode="edit"
        />
      </div>
    </div>
  );
}