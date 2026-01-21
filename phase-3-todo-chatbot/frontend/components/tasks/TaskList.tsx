'use client';

import { Task } from '@/types/models';
import { TaskCard } from '@/components/tasks/TaskCard';
import { TaskFilters } from '@/components/tasks/TaskFilters';
import { useMemo } from 'react';

interface TaskListProps {
  tasks: Task[];
  onToggleComplete: (taskId: string, checked: boolean) => void;
  onTaskDelete: (taskId: string) => Promise<void>;
  onEditTask: (task: Task) => void;
  statusFilter: Task['status'] | 'all';
  searchQuery: string;
  onStatusChange: (value: Task['status'] | 'all') => void;
  onSearchChange: (value: string) => void;
}

export const TaskList = ({ tasks, onToggleComplete, onTaskDelete, onEditTask, statusFilter, searchQuery, onStatusChange, onSearchChange }: TaskListProps) => {
  const filteredTasks = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    return tasks.filter((task) => {
      const matchesStatus = statusFilter === 'all' || task.status === statusFilter;
      const matchesQuery = query
        ? task.title.toLowerCase().includes(query) || (task.description ?? '').toLowerCase().includes(query)
        : true;
      return matchesStatus && matchesQuery;
    });
  }, [tasks, statusFilter, searchQuery]);

  return (
    <div className="space-y-4">
      <TaskFilters
        statusFilter={statusFilter}
        searchQuery={searchQuery}
        onStatusChange={onStatusChange}
        onSearchChange={onSearchChange}
      />
      <div className="space-y-3">
        {filteredTasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onToggleComplete={onToggleComplete}
            onTaskDelete={onTaskDelete}
            onEditTask={onEditTask}
          />
        ))}
      </div>
    </div>
  );
};