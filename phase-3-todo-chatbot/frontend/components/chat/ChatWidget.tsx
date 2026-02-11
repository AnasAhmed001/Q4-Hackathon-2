'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { useSession } from '@/lib/auth';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { Message } from '@/components/chat/Message';
import { MessageInput } from '@/components/chat/MessageInput';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

const QUICK_PROMPTS = [
  { icon: '✏️', text: 'Create a task for tomorrow' },
  { icon: '📋', text: 'Show me my tasks' },
  { icon: '✅', text: 'Mark a task complete' },
  { icon: '🗑️', text: 'Delete a task' },
];

const ChatWidget = () => {
  const { data: session, isPending } = useSession();
  const userId = session?.user?.id || '';

  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>();
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  /* ── persistence keys ── */
  const storageKey = useMemo(() => (userId ? `chatMessages:${userId}` : 'chatMessages'), [userId]);
  const conversationKey = useMemo(
    () => (userId ? `currentConversationId:${userId}` : 'currentConversationId'),
    [userId],
  );

  /* ── restore from localStorage ── */
  useEffect(() => {
    if (!userId || typeof window === 'undefined') return;
    const saved = localStorage.getItem(storageKey);
    const savedConv = localStorage.getItem(conversationKey);
    if (saved) {
      try { setMessages(JSON.parse(saved)); } catch { localStorage.removeItem(storageKey); }
    }
    if (savedConv) setCurrentConversationId(savedConv);
  }, [userId, storageKey, conversationKey]);

  /* ── persist messages ── */
  useEffect(() => {
    if (!userId || typeof window === 'undefined') return;
    localStorage.setItem(storageKey, JSON.stringify(messages));
  }, [messages, storageKey, userId]);

  /* ── persist conversation id ── */
  useEffect(() => {
    if (!userId || typeof window === 'undefined') return;
    currentConversationId
      ? localStorage.setItem(conversationKey, currentConversationId)
      : localStorage.removeItem(conversationKey);
  }, [currentConversationId, conversationKey, userId]);

  /* ── auto-scroll (only when there are messages) ── */
  useEffect(() => {
    if (messages.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isSending, isOpen]);

  /* ── load history ── */
  useEffect(() => {
    if (!isOpen || !userId || !currentConversationId || messages.length > 0) return;
    (async () => {
      try {
        const url = new URL('/api/chat/history', window.location.origin);
        url.searchParams.set('userId', userId);
        url.searchParams.set('conversationId', currentConversationId);
        const res = await fetch(url.toString(), { method: 'GET', cache: 'no-store' });
        if (!res.ok) return;
        const data = await res.json();
        setMessages(
          (data?.messages || []).map((m: any) => ({
            id: m.id, role: m.role, content: m.content, created_at: m.created_at,
          })),
        );
      } catch (err) {
        console.error('Error loading conversation history:', err);
      }
    })();
  }, [isOpen, userId, currentConversationId, messages.length]);

  /* ── send ── */
  const handleSend = async () => {
    if (!inputValue.trim() || isSending || !userId) return;
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setIsSending(true);
    setError(null);
    try {
      const res = await fetch('/api/chat/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId, message: userMsg.content, conversationId: currentConversationId }),
      });
      if (!res.ok) throw new Error((await res.text().catch(() => '')) || `Request failed (${res.status})`);
      const data = await res.json();
      if (data?.conversation_id && data.conversation_id !== currentConversationId)
        setCurrentConversationId(data.conversation_id);
      if (data?.response) {
        setMessages((prev) => [
          ...prev,
          { id: `assistant-${Date.now()}`, role: 'assistant', content: data.response, created_at: new Date().toISOString() },
        ]);
      }

      // If any task-mutating tool was called, build optimistic detail & notify
      const TASK_TOOLS = ['add_task', 'update_task', 'complete_task', 'delete_task'];
      const calls = data?.tool_calls as Array<{ name?: string; arguments?: Record<string, any> }> | undefined;
      const responses = data?.tool_responses as Array<{ name?: string; output?: string }> | undefined;
      if (calls?.some((tc) => TASK_TOOLS.includes(tc.name ?? ''))) {
        const ops = calls
          .filter((tc) => TASK_TOOLS.includes(tc.name ?? ''))
          .map((tc, i) => {
            let output: Record<string, any> = {};
            try { output = JSON.parse(responses?.[i]?.output ?? '{}'); } catch {}
            return { tool: tc.name!, args: tc.arguments ?? {}, result: output };
          });
        window.dispatchEvent(new CustomEvent('tasks-updated', { detail: { ops, userId } }));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const handleNewChat = () => { setMessages([]); setCurrentConversationId(undefined); setError(null); };

  if (isPending || !userId) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col items-end gap-3 sm:bottom-6 sm:right-6">
      {/* ── Chat panel ── */}
      {isOpen && (
        <Card
          className={cn(
            'flex flex-col overflow-hidden border border-border/60 bg-background/95 p-0 shadow-2xl backdrop-blur-xl',
            // responsive: full-screen on mobile, fixed size on desktop
            'fixed inset-0 z-50 rounded-none sm:static sm:inset-auto sm:h-[480px] sm:w-[400px] sm:rounded-2xl md:h-[500px] md:w-[420px]',
          )}
        >
          {/* ── Header ── */}
          <CardHeader className="sticky top-0 z-10 shrink-0 gap-0 border-b border-border/40 bg-card px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                {/* Bot icon */}
                <div className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="size-4">
                    <path d="M12 8V4H8" /><rect width="16" height="12" x="4" y="8" rx="2" /><path d="M2 14h2" /><path d="M20 14h2" /><path d="M15 13v2" /><path d="M9 13v2" />
                  </svg>
                </div>
                <div className="leading-tight">
                  <CardTitle className="text-sm font-semibold">Task Assistant</CardTitle>
                  <p className="text-[11px] text-muted-foreground">Always ready to help</p>
                </div>
              </div>

              <div className="flex items-center gap-1">
                <Badge variant="outline" className="h-5 gap-1 border-green-500/30 px-1.5 text-[10px] text-green-600 dark:text-green-400">
                  <span className="size-1.5 rounded-full bg-green-500" />
                  Online
                </Badge>

                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="ghost" size="icon-sm" onClick={handleNewChat} className="text-muted-foreground hover:text-foreground">
                      {/* Plus icon */}
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="size-4"><path d="M5 12h14" /><path d="M12 5v14" /></svg>
                      <span className="sr-only">New conversation</span>
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">New chat</TooltipContent>
                </Tooltip>

                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="ghost" size="icon-sm" onClick={() => setIsOpen(false)} className="text-muted-foreground hover:text-foreground">
                      {/* X icon */}
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="size-4"><path d="M18 6 6 18" /><path d="m6 6 12 12" /></svg>
                      <span className="sr-only">Close chat</span>
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="bottom">Close</TooltipContent>
                </Tooltip>
              </div>
            </div>
          </CardHeader>

          {/* ── Messages ── */}
          <ScrollArea ref={scrollAreaRef} className="flex-1">
            <CardContent className="flex flex-col gap-3 px-4 py-4">
              {messages.length === 0 ? (
                <div className="flex h-full flex-col items-center justify-center gap-5 py-8 text-center">
                  {/* Empty state */}
                  <div className="flex size-14 items-center justify-center rounded-2xl bg-muted">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" className="size-7 text-muted-foreground">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                    </svg>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-foreground">How can I help?</p>
                    <p className="text-xs text-muted-foreground">Manage tasks using natural language.</p>
                  </div>
                  <div className="grid w-full grid-cols-2 gap-2">
                    {QUICK_PROMPTS.map((p) => (
                      <button
                        key={p.text}
                        type="button"
                        onClick={() => setInputValue(p.text)}
                        className="flex items-center gap-2 rounded-xl border border-border/60 bg-card px-3 py-2.5 text-left text-xs text-foreground transition-colors hover:bg-accent"
                      >
                        <span className="text-base leading-none">{p.icon}</span>
                        <span className="line-clamp-2">{p.text}</span>
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                messages.map((message) => (
                  <Message key={message.id} role={message.role} content={message.content} timestamp={message.created_at} />
                ))
              )}
              {isSending && (
                <Message role="assistant" content="" timestamp={new Date().toISOString()} isLoading />
              )}
              <div ref={messagesEndRef} />
            </CardContent>
          </ScrollArea>

          {/* ── Footer input ── */}
          <Separator />
          <CardFooter className="shrink-0 sticky bottom-0 flex-col gap-2 bg-card/80 px-3 py-3 backdrop-blur-sm">
            {error && (
              <div className="flex w-full items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-xs text-destructive">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="size-3.5 shrink-0"><circle cx="12" cy="12" r="10" /><path d="M12 8v4" /><path d="M12 16h.01" /></svg>
                <span className="line-clamp-2">{error}</span>
              </div>
            )}
            <MessageInput
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              onSend={handleSend}
              disabled={isSending}
              placeholder="Message Task Assistant…"
            />
            <p className="text-center text-[10px] text-muted-foreground/60">
              Press Enter to send · Shift + Enter for new line
            </p>
          </CardFooter>
        </Card>
      )}

      {/* ── FAB trigger ── */}
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            size="icon-lg"
            onClick={() => setIsOpen((prev) => !prev)}
            className={cn(
              'size-14 rounded-full shadow-lg transition-transform hover:scale-105 active:scale-95',
              isOpen && 'rotate-90',
            )}
          >
            {isOpen ? (
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="size-5"><path d="M18 6 6 18" /><path d="m6 6 12 12" /></svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="size-5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
            )}
            <span className="sr-only">{isOpen ? 'Close chat' : 'Open chat'}</span>
          </Button>
        </TooltipTrigger>
        <TooltipContent side="left">{isOpen ? 'Close chat' : 'Open chat'}</TooltipContent>
      </Tooltip>
    </div>
  );
};

export { ChatWidget };
