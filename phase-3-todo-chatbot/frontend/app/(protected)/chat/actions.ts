'use server';

import { cookies } from 'next/headers';
import { ChatResponse, ConversationHistoryResponse } from '@/types/api';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';
const AUTH_URL = process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

async function serializeRequestCookies() {
  const jar = await cookies();
  const all = jar.getAll();
  return all.length ? all.map((c) => `${c.name}=${c.value}`).join('; ') : '';
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

export async function sendChatMessageAction(userId: string, message: string, conversationId?: string): Promise<ChatResponse> {
  return authFetch<ChatResponse>(`/api/${userId}/chat`, {
    method: 'POST',
    body: {
      message,
      conversation_id: conversationId,
    },
  });
}

export async function getConversationHistoryAction(
  userId: string,
  conversationId: string,
  params?: { skip?: number; limit?: number }
): Promise<ConversationHistoryResponse> {
  const search = new URLSearchParams();
  if (params?.skip !== undefined) search.set('skip', String(params.skip));
  if (params?.limit !== undefined) search.set('limit', String(params.limit));
  const qs = search.toString();

  return authFetch<ConversationHistoryResponse>(
    `/api/${userId}/conversations/${conversationId}${qs ? `?${qs}` : ''}`
  );
}
