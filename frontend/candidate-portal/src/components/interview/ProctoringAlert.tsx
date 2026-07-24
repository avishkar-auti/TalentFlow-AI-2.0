import React from 'react';
import { AlertTriangle, AlertOctagon, Volume2 } from 'lucide-react';

interface ProctoringAlertProps {
  message: string | null;
  warningCount?: number;
  maxWarnings?: number;
  alertType?: 'vision' | 'audio' | 'termination';
}

export function ProctoringAlert({
  message,
  warningCount = 0,
  maxWarnings = 5,
  alertType = 'vision'
}: ProctoringAlertProps) {
  if (!message) return null;

  const isSevere = warningCount >= 4 || alertType === 'termination';

  return (
    <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-20 animate-bounce transition-all">
      <div className={`backdrop-blur-md px-5 py-2.5 rounded-full shadow-2xl flex items-center gap-3 border text-sm font-semibold ${
        isSevere
          ? 'bg-red-600/95 border-red-400 text-white shadow-red-500/50'
          : alertType === 'audio'
          ? 'bg-amber-600/90 border-amber-400 text-white shadow-amber-500/40'
          : 'bg-amber-500/95 border-amber-300 text-white shadow-amber-500/40'
      }`}>
        {alertType === 'audio' ? (
          <Volume2 className="h-5 w-5 animate-pulse" />
        ) : isSevere ? (
          <AlertOctagon className="h-5 w-5 animate-pulse text-white" />
        ) : (
          <AlertTriangle className="h-5 w-5 text-white" />
        )}

        {warningCount > 0 && alertType !== 'audio' && (
          <span className="bg-black/30 px-2 py-0.5 rounded-md text-xs font-mono font-bold tracking-wide">
            WARNING [{warningCount}/{maxWarnings}]
          </span>
        )}

        <span>{message}</span>
      </div>
    </div>
  );
}
