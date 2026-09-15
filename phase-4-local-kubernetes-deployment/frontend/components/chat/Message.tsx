'use client';

import { cn } from '@/lib/utils';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Skeleton } from '@/components/ui/skeleton';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  isLoading?: boolean;
}

function formatTime(timestamp: string) {
  try {
    return new Intl.DateTimeFormat(undefined, {
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(timestamp));
  } catch {
    return '';
  }
}

const Message = ({ role, content, timestamp, isLoading = false }: MessageProps) => {
  const isUser = role === 'user';

  return (
    <div className={cn('group flex items-end gap-2', isUser && 'flex-row-reverse')}>
      {/* Avatar */}
      <Avatar size="sm" className="mb-1 shrink-0">
        <AvatarFallback
          className={cn(
            'text-[10px] font-semibold',
            isUser
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-muted-foreground'
          )}
        >
          {isUser ? 'U' : 'AI'}
        </AvatarFallback>
      </Avatar>

      {/* Bubble */}
      <div
        className={cn(
          'relative max-w-[80%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed shadow-sm',
          isUser
            ? 'rounded-br-md bg-primary text-primary-foreground'
            : 'rounded-bl-md bg-muted text-foreground'
        )}
      >
        {isLoading ? (
          <div className="flex flex-col gap-1.5 py-0.5">
            <Skeleton className="h-3 w-36 rounded-full bg-muted-foreground/20" />
            <Skeleton className="h-3 w-24 rounded-full bg-muted-foreground/20" />
          </div>
        ) : (
          <div className="whitespace-pre-wrap break-words">{content}</div>
        )}

        {/* Timestamp — appears on hover */}
        {!isLoading && (
          <span
            className={cn(
              'mt-1 block text-[10px] leading-none opacity-0 transition-opacity group-hover:opacity-100',
              isUser ? 'text-primary-foreground/60' : 'text-muted-foreground'
            )}
          >
            {formatTime(timestamp)}
          </span>
        )}
      </div>
    </div>
  );
};

export { Message };