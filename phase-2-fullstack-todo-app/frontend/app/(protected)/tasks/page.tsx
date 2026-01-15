import { TasksClient } from '@/components/tasks/TasksClient';
import { auth } from '@/lib/auth-server';
import { Task } from '@/types/models';
import { Metadata } from 'next';
import { headers } from 'next/headers';

export const metadata: Metadata = {
  title: 'Tasks Manager',
  description: 'Manage your tasks',
};

export default async function TasksPage() {
  // Get session - proxy.ts already ensures authentication
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  // Server-side data fetching
  const initialTasks: Task[] = []; // client will fetch with auth token

  return <TasksClient initialTasks={initialTasks} userId={session?.user.id || ''} />;
}