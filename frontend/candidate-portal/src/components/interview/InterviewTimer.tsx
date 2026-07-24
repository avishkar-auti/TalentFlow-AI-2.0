import React, { useState, useEffect } from 'react';
import { Clock } from 'lucide-react';
import { formatTime } from '../../utils/formatters';

interface InterviewTimerProps {
  isActive: boolean;
}

export function InterviewTimer({ isActive }: InterviewTimerProps) {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    
    if (isActive) {
      interval = setInterval(() => {
        setSeconds(s => s + 1);
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [isActive]);

  return (
    <div className="flex items-center gap-1.5 text-sm font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 px-3 py-1 rounded-full">
      <Clock className="h-4 w-4" />
      {formatTime(seconds)}
    </div>
  );
}
