'use client';

import { Task } from '@/types/models';
import { TaskCard } from '@/components/tasks/TaskCard';
import { TaskFilters } from '@/components/tasks/TaskFilters';

interface TaskListProps {
  tasks: Task[];
  onTaskUpdate: () => void;
  onTaskDelete: () => void;
}

export const TaskList = ({ tasks, onTaskUpdate, onTaskDelete }: TaskListProps) => {
  return (
    <div className="space-y-4">
      <TaskFilters />
      <div className="space-y-3">
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onTaskUpdate={onTaskUpdate}
            onTaskDelete={onTaskDelete}
          />
        ))}
      </div>
    </div>
  );
};