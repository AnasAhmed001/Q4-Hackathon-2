import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';
const AUTH_URL = process.env.BETTER_AUTH_URL || process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000';

async function getTokenFromCookie(cookieHeader: string | null) {
  const res = await fetch(`${AUTH_URL}/api/auth/token`, {
    headers: cookieHeader ? { cookie: cookieHeader } : {},
    cache: 'no-store',
  });

  if (!res.ok) {
    const errText = await res.text().catch(() => '');
    return { token: null as string | null, error: errText || `token fetch failed (${res.status})`, status: res.status };
  }

  const data = await res.json().catch(() => null);
  const token = data?.token as string | undefined;
  if (!token) {
    return { token: null as string | null, error: 'No token returned', status: 401 };
  }

  return { token, error: null as string | null, status: 200 };
}

export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    const userId = url.searchParams.get('userId') || undefined;
    const conversationId = url.searchParams.get('conversationId') || undefined;

    if (!userId || !conversationId) {
      return NextResponse.json({ error: 'Missing userId or conversationId' }, { status: 400 });
    }

    const cookieHeader = request.headers.get('cookie');
    const { token, error, status } = await getTokenFromCookie(cookieHeader);
    if (!token) {
      return NextResponse.json({ error: error || 'Unauthorized' }, { status });
    }

    const backendRes = await fetch(
      `${BACKEND_URL}/api/${encodeURIComponent(userId)}/conversations/${encodeURIComponent(conversationId)}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        cache: 'no-store',
      }
    );

    const text = await backendRes.text();
    const payload = text ? JSON.parse(text) : {};

    return NextResponse.json(payload, { status: backendRes.status });
  } catch (err) {
    console.error('[api/chat/history] error', err);
    return NextResponse.json({ error: 'Internal error' }, { status: 500 });
  }
}
