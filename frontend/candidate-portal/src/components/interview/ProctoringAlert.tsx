import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface ProctoringAlertProps {
  message: string | null;
}

export function ProctoringAlert({ message }: ProctoringAlertProps) {
  if (!message) return null;

  return (
    <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10 animate-fade-in">
      <div className="bg-yellow-500/90 backdrop-blur-sm text-white px-4 py-2 rounded-full shadow-lg flex items-center gap-2 text-sm font-medium">
        <AlertTriangle className="h-4 w-4" />
        {message}
      </div>
    </div>
  );
}
