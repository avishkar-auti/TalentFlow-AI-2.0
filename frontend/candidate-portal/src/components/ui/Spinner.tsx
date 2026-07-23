import React from 'react';
import { cn } from './Button';

interface SpinnerProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function Spinner({ className, size = 'md' }: SpinnerProps) {
  const sizes = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-3',
    lg: 'h-12 w-12 border-4'
  };

  return (
    <div className="flex justify-center items-center">
      <div 
        className={cn(
          "animate-spin rounded-full border-t-primary-500 border-gray-200 dark:border-gray-700",
          sizes[size],
          className
        )} 
      />
    </div>
  );
}
