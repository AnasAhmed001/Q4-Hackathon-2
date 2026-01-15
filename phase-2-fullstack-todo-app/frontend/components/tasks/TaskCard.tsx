'use client';

import { Task } from '@/types/models';
import { formatDate } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { useState } from 'react';
import { DeleteConfirmDialog } from '@/components/tasks/DeleteConfirmDialog';

interface TaskCardProps {
  task: Task;
  onToggleComplete: (taskId: string, checked: boolean) => void;
  onTaskDelete: (taskId: string) => Promise<void>;
  onEditTask: (task: Task) => void;
}

export const TaskCard = ({ task, onToggleComplete, onTaskDelete, onEditTask }: TaskCardProps) => {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleStatusChange = async (checked: boolean) => {
    onToggleComplete(task.id, checked);
  };

  const handleEdit = () => {
    onEditTask(task);
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await onTaskDelete(task.id);
    } finally {
      setDeleting(false);
      setDeleteDialogOpen(false);
    }
  };

  return (
    <>
      <div
        className={`border rounded-lg p-4 shadow-sm transition-all ${
          task.status === 'completed' ? 'bg-muted border-border' : 'bg-card border-border'
        }`}
      >
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
              task.status === 'completed' ? 'line-through text-muted-foreground' : 'text-foreground'
            }`}>
              {task.title}
            </h3>

            {task.description && (
              <p className={`mt-1 text-sm ${
                task.status === 'completed' ? 'line-through text-muted-foreground' : 'text-muted-foreground'
              }`}>
                {task.description}
              </p>
            )}

            {task.dueDate && (
              <p className="mt-2 text-xs text-muted-foreground">
                Due: {formatDate(task.dueDate)}
              </p>
            )}

            <p className="mt-2 text-xs text-muted-foreground">
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