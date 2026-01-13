'use client';

import { useState } from 'react';
import { Task } from '@/types/models';
import { apiClient } from '@/lib/api-client';
import { TaskForm } from '@/components/tasks/TaskForm';
import { useRouter } from 'next/navigation';

export default function NewTaskPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const router = useRouter();

  const handleSubmit = async (taskData: Partial<Task>) => {
    setLoading(true);
    setError(null);

    try {
      await apiClient.post('/tasks', taskData);
      // Redirect to tasks list after successful creation
      router.push('/tasks');
      router.refresh(); // Refresh to update the UI
    } catch (err) {
      setError('Failed to create task. Please try again.');
      console.error('Error creating task:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    router.push('/tasks');
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Create New Task</h1>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">Error! </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      <div className="bg-white p-6 rounded-lg shadow-md">
        <TaskForm
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          mode="create"
        />
      </div>
    </div>
  );
}