'use client';

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { TaskStatus } from '@/types/models';

interface TaskFiltersProps {
  statusFilter: TaskStatus | 'all';
  searchQuery: string;
  onStatusChange: (value: TaskStatus | 'all') => void;
  onSearchChange: (value: string) => void;
}

export const TaskFilters = ({ statusFilter, searchQuery, onStatusChange, onSearchChange }: TaskFiltersProps) => {

  return (
    <div className="flex flex-col sm:flex-row gap-4 mb-6">
      <div className="flex-1">
        <Input
          placeholder="Search tasks..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>
      <div className="w-full sm:w-auto">
        <Select value={statusFilter} onValueChange={(value: TaskStatus | 'all') => onStatusChange(value)}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Tasks</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};