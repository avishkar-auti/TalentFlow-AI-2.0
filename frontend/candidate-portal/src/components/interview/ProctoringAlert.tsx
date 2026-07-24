import React, { useEffect } from 'react';
import { AlertTriangle, AlertOctagon, Volume2, UserCheck, Info, X } from 'lucide-react';

interface ProctoringAlertProps {
  message: string | null;
  warningCount?: number;
  maxWarnings?: number;
  alertType?: 'vision' | 'audio' | 'termination' | 'peer' | 'info';
  onClose?: () => void;
  autoCloseMs?: number;
}

export function ProctoringAlert({
  message,
  warningCount = 0,
  maxWarnings = 5,
  alertType = 'vision',
  onClose,
  autoCloseMs = 5000
}: ProctoringAlertProps) {
  useEffect(() => {
    if (!message || !onClose || alertType === 'termination') return;
    const timer = setTimeout(() => {
      onClose();
    }, autoCloseMs);
    return () => clearTimeout(timer);
  }, [message, alertType, onClose, autoCloseMs]);

  if (!message) return null;

  const isSevere = warningCount >= 4 || alertType === 'termination';

  let bgStyle = 'bg-amber-500/95 border-amber-300 text-white shadow-amber-500/40';
  let Icon = AlertTriangle;

  if (alertType === 'peer') {
    bgStyle = 'bg-indigo-600/95 border-indigo-400 text-white shadow-indigo-500/50';
    Icon = UserCheck;
  } else if (alertType === 'info') {
    bgStyle = 'bg-blue-600/95 border-blue-400 text-white shadow-blue-500/40';
    Icon = Info;
  } else if (alertType === 'audio') {
    bgStyle = 'bg-amber-600/95 border-amber-400 text-white shadow-amber-500/40';
    Icon = Volume2;
  } else if (isSevere) {
    bgStyle = 'bg-red-600/95 border-red-400 text-white shadow-red-500/50 animate-pulse';
    Icon = AlertOctagon;
  }

  return (
    <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-40 transition-all duration-300">
      <div className={`backdrop-blur-md px-5 py-2.5 rounded-full shadow-2xl flex items-center gap-3 border text-sm font-semibold ${bgStyle}`}>
        <Icon className={`h-5 w-5 shrink-0 ${isSevere || alertType === 'audio' ? 'animate-pulse' : ''}`} />

        {warningCount > 0 && alertType === 'vision' && (
          <span className="bg-black/30 px-2 py-0.5 rounded-md text-xs font-mono font-bold tracking-wide">
            WARNING [{warningCount}/{maxWarnings}]
          </span>
        )}

        <span className="leading-tight">{message}</span>

        {onClose && (
          <button
            onClick={onClose}
            className="ml-1 p-0.5 hover:bg-white/20 rounded-full transition-colors shrink-0"
            title="Dismiss alert"
          >
            <X className="w-4 h-4 text-white/80 hover:text-white" />
          </button>
        )}
      </div>
    </div>
  );
}
