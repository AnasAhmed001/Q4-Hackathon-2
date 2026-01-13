'use client';

import { Task } from '@/types/models';
import { formatDate } from '@/lib/utils';
import { apiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { DeleteConfirmDialog } from '@/components/tasks/DeleteConfirmDialog';

interface TaskCardProps {
  task: Task;
  onTaskUpdate: () => void;
  onTaskDelete: () => void;
}

export const TaskCard = ({ task, onTaskUpdate, onTaskDelete }: TaskCardProps) => {
  const router = useRouter();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleStatusChange = async (checked: boolean) => {
    try {
      await apiClient.put(`/tasks/${task.id}`, {
        status: checked ? 'completed' : 'pending'
      });
      onTaskUpdate();
    } catch (error) {
      console.error('Failed to update task status:', error);
      // Optionally show an error message to the user
    }
  };

  const handleEdit = () => {
    router.push(`/tasks/${task.id}/edit`);
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await apiClient.delete(`/tasks/${task.id}`);
      onTaskDelete();
    } catch (error) {
      console.error('Failed to delete task:', error);
      // Optionally show an error message to the user
    } finally {
      setDeleting(false);
      setDeleteDialogOpen(false);
    }
  };

  return (
    <>
      <div className={`border rounded-lg p-4 shadow-sm transition-all ${
        task.status === 'completed' ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'
      }`}>
        <div className="flex items-start gap-4">
          <div className="flex items-center pt-1">
            <Checkbox
              checked={task.status === 'completed'}
              onCheckedChange={handleStatusChange}
              aria-label={`Mark task "${task.title}" as ${task.status === 'completed' ? 'incomplete' : 'complete'}`}
            />
          </div>

          <div className="flex-1 min-w-0">
            <h3 className={`text-lg font-medium ${
              task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900'
            }`}>
              {task.title}
            </h3>

            {task.description && (
              <p className={`mt-1 text-sm ${
                task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-600'
              }`}>
                {task.description}
              </p>
            )}

            {task.dueDate && (
              <p className="mt-2 text-xs text-gray-500">
                Due: {formatDate(task.dueDate)}
              </p>
            )}

            <p className="mt-2 text-xs text-gray-500">
              Created: {formatDate(task.createdAt)}
            </p>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleEdit}>
              Edit
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setDeleteDialogOpen(true)}
              className="text-red-600 hover:text-red-700"
            >
              Delete
            </Button>
          </div>
        </div>
      </div>

      <DeleteConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={handleDelete}
        taskTitle={task.title}
        loading={deleting}
      />
    </>
  );
};