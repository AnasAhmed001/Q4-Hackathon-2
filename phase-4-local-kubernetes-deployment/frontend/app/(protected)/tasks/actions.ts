'use server';

import { cookies } from 'next/headers';
import { Task } from '@/types/models';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';
const AUTH_URL = process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

async function serializeRequestCookies() {
  const jar = await cookies();
  const all = jar.getAll();
  return all.length ? all.map((c: { name: string; value: string }) => `${c.name}=${c.value}`).join('; ') : '';
}

async function getServerToken() {
  const cookieHeader = await serializeRequestCookies();
  const res = await fetch(`${AUTH_URL}/api/auth/token`, {
    headers: {
      cookie: cookieHeader,
    },
    cache: 'no-store',
  });

  if (!res.ok) {
    const errText = await res.text().catch(() => '');
    console.error('[auth] token fetch failed', res.status, errText?.slice(0, 200));
    throw new Error(`Failed to get auth token (${res.status})`);
  }

  const data = await res.json();
  if (!data?.token) {
    throw new Error('No token returned from auth service');
  }
  return data.token as string;
}

async function authFetch<T>(path: string, options: { method?: HttpMethod; body?: any } = {}): Promise<T> {
  const token = await getServerToken();
  const { method = 'GET', body } = options;

  // Temporary: sanity-check auth header presence without leaking full token
  console.log('[authFetch] token prefix', token ? token.slice(0, 8) : 'missing');

  const res = await fetch(`${BACKEND_URL}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: body ? JSON.stringify(body) : undefined,
    cache: 'no-store',
  });

  if (!res.ok) {
    const errText = await res.text().catch(() => '');
    console.error('[backend] request failed', res.status, errText?.slice(0, 200));
    throw new Error(`Backend request failed (${res.status}): ${errText || res.statusText}`);
  }

  if (res.status === 204) return {} as T;
  return (await res.json()) as T;
}

function mapTaskFromApi(apiTask: any): Task {
  return {
    id: apiTask.id,
    title: apiTask.title,
    description: apiTask.description || '',
    status: apiTask.status || 'pending',
    completed: (apiTask.status || 'pending') === 'completed',
    dueDate: apiTask.due_date || apiTask.dueDate || null,
    userId: apiTask.user_id || apiTask.userId,
    createdAt: apiTask.created_at || apiTask.createdAt,
    updatedAt: apiTask.updated_at || apiTask.updatedAt,
  } as Task;
}

export async function getTasksAction(userId: string): Promise<Task[]> {
  const res = await authFetch<{ tasks?: any[] } | any[]>(`/api/${userId}/tasks`);
  const tasks = Array.isArray(res) ? res : res.tasks || [];
  return tasks.map(mapTaskFromApi);
}

export async function createTaskAction(userId: string, payload: {
  title: string;
  description?: string;
  status?: string;
  dueDate?: string;
}): Promise<Task> {
  const body = {
    title: payload.title,
    description: payload.description,
    status: payload.status || 'pending',
    due_date: payload.dueDate || null,
  };
  const res = await authFetch<any>(`/api/${userId}/tasks`, { method: 'POST', body });
  return mapTaskFromApi(res);
}

export async function updateTaskAction(
  userId: string,
  taskId: string,
  updates: {
    title?: string;
    description?: string;
    status?: string;
    dueDate?: string;
  }
): Promise<Task> {
  const body = {
    title: updates.title,
    description: updates.description,
    status: updates.status,
    due_date: updates.dueDate,
  };
  const res = await authFetch<any>(`/api/${userId}/tasks/${taskId}`, { method: 'PUT', body });
  return mapTaskFromApi(res);
}

export async function deleteTaskAction(userId: string, taskId: string): Promise<void> {
  await authFetch<void>(`/api/${userId}/tasks/${taskId}`, { method: 'DELETE' });
}
