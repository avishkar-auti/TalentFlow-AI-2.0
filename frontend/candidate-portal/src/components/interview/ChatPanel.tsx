import React, { useEffect, useRef } from 'react';
import type { InterviewMessage } from '../../types';
import { cn } from '../ui/Button';

interface ChatPanelProps {
  messages: InterviewMessage[];
}

export function ChatPanel({ messages }: ChatPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
      {messages.length === 0 && (
        <div className="text-center text-gray-500 dark:text-gray-400 mt-10">
          The interview will begin shortly...
        </div>
      )}
      
      {messages.map((msg) => (
        <div 
          key={msg.id}
          className={cn(
            "max-w-[85%] rounded-2xl px-4 py-3",
            msg.sender === 'interviewer' 
              ? "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200 self-start mr-auto" 
              : "bg-primary-600 text-white self-end ml-auto"
          )}
        >
          <div className="text-xs opacity-70 mb-1">
            {msg.sender === 'interviewer' ? 'Interviewer' : 'You'}
          </div>
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
        </div>
      ))}
    </div>
  );
}
