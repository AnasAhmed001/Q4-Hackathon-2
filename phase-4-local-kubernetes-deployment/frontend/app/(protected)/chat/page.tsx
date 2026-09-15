'use client';

import { useEffect } from 'react';
import { useSession } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

const features = [
  {
    icon: '⚡',
    title: 'Instant task capture',
    description: 'Create, update, and complete tasks using plain language.',
  },
  {
    icon: '📋',
    title: 'Smart queries',
    description: 'Ask about upcoming deadlines or overdue items.',
  },
  {
    icon: '🔄',
    title: 'Always available',
    description: 'The widget follows you across every page.',
  },
  {
    icon: '🎯',
    title: 'Context-aware',
    description: 'Remembers your conversation for follow-ups.',
  },
];

const examplePrompts = [
  'Create a task to finalize the roadmap by Friday.',
  'Show tasks due tomorrow.',
  'Complete the onboarding checklist task.',
  'Delete the duplicate meeting task.',
];

const ChatPage = () => {
  const { data: session, isPending } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (!isPending && !session) {
      router.push('/login');
    }
  }, [isPending, session, router]);

  if (isPending) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-foreground" />
      </div>
    );
  }

  if (!session?.user?.id) {
    return null;
  }

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6 px-4 pb-8">
      {/* Hero card */}
      <Card className="relative overflow-hidden border-0 bg-primary text-primary-foreground shadow-xl">
        {/* Decorative blurred circles */}
        <div className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-primary-foreground/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-12 -left-12 h-36 w-36 rounded-full bg-primary-foreground/10 blur-2xl" />

        <CardHeader className="relative z-10">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Avatar className="h-10 w-10 bg-primary-foreground/20">
                <AvatarFallback className="bg-transparent text-lg">
                  🤖
                </AvatarFallback>
              </Avatar>
              <div>
                <CardTitle className="text-2xl font-bold tracking-tight">
                  Chat Assistant
                </CardTitle>
                <CardDescription className="text-primary-foreground/80">
                  Capture tasks at the speed of thought
                </CardDescription>
              </div>
            </div>
            <Badge
              variant="secondary"
              className="bg-primary-foreground/15 text-primary-foreground backdrop-blur-sm"
            >
              <span className="mr-1.5 inline-block h-2 w-2 rounded-full bg-green-400" />
              Online
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="relative z-10 space-y-5">
          <p className="text-sm leading-relaxed text-primary-foreground/85">
            The chatbot lives in the bottom-right corner so it stays with you
            while you manage tasks. Open the widget to start a conversation,
            minimize it when you need focus, and come back whenever a new task
            pops into your head.
          </p>

          <Separator className="bg-primary-foreground/15" />

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {features.map((f) => (
              <div
                key={f.title}
                className="flex items-start gap-3 rounded-xl bg-primary-foreground/10 p-3 backdrop-blur-sm transition-colors hover:bg-primary-foreground/15"
              >
                <span className="text-lg">{f.icon}</span>
                <div>
                  <p className="text-sm font-medium">{f.title}</p>
                  <p className="text-xs text-primary-foreground/70">
                    {f.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Example prompts */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Try saying&hellip;</CardTitle>
          <CardDescription>
            Click a prompt or open the widget and type your own.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {examplePrompts.map((prompt) => (
            <Badge
              key={prompt}
              variant="outline"
              className="cursor-default select-text border-border bg-muted/50 text-foreground"
            >
              &ldquo;{prompt}&rdquo;
            </Badge>
          ))}
        </CardContent>
      </Card>

      {/* Navigation */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Need a full workspace view?</CardTitle>
          <CardDescription>
            Keep planning inside Tasks and let the widget handle quick updates
            from anywhere.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Link href="/tasks">
            <Button>Go to Tasks</Button>
          </Link>
          <Button
            variant="outline"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          >
            Back to top
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default ChatPage;