'use client';

import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

interface MessageInputProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
  onSend: () => void;
  disabled: boolean;
  placeholder: string;
}

const MessageInput = ({
  value,
  onChange,
  onKeyDown,
  onSend,
  disabled,
  placeholder,
}: MessageInputProps) => {
  return (
    <div className="flex w-full items-end gap-2">
      <Textarea
        value={value}
        onChange={onChange}
        onKeyDown={onKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className="min-h-[40px] max-h-28 flex-1 resize-none rounded-xl border-border/60 bg-muted/40 px-3 py-2.5 text-sm shadow-none transition-colors placeholder:text-muted-foreground/60 focus-visible:bg-background focus-visible:ring-1"
      />

      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            size="icon"
            onClick={onSend}
            disabled={disabled || !value.trim()}
            className="shrink-0 rounded-xl"
          >
            {/* Send arrow icon */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
              className="size-4"
            >
              <path d="M5 12h14" />
              <path d="m12 5 7 7-7 7" />
            </svg>
            <span className="sr-only">Send message</span>
          </Button>
        </TooltipTrigger>
        <TooltipContent side="top">Send message</TooltipContent>
      </Tooltip>
    </div>
  );
};

export { MessageInput };