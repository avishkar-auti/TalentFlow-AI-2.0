import React from 'react';
import { ShieldCheck, Eye, UserX, Users, AlertTriangle, EyeOff } from 'lucide-react';

interface VisionStatusBadgeProps {
  activeFlags: string[];
  className?: string;
}

const FLAG_INFO: Record<string, { label: string; color: string; pulse: string; Icon: React.FC<any> }> = {
  gaze_away_from_screen: {
    label: 'Looking Away',
    color: '#F59E0B',
    pulse: 'rgba(245,158,11,0.4)',
    Icon: Eye,
  },
  head_turned_away: {
    label: 'Head Turned',
    color: '#F97316',
    pulse: 'rgba(249,115,22,0.4)',
    Icon: UserX,
  },
  no_face_detected: {
    label: 'No Face',
    color: '#EF4444',
    pulse: 'rgba(239,68,68,0.4)',
    Icon: UserX,
  },
  multiple_faces_detected: {
    label: 'Multiple Faces',
    color: '#DC2626',
    pulse: 'rgba(220,38,38,0.4)',
    Icon: Users,
  },
  identity_mismatch: {
    label: 'ID Mismatch',
    color: '#7C3AED',
    pulse: 'rgba(124,58,237,0.4)',
    Icon: AlertTriangle,
  },
  eyes_closed_extended: {
    label: 'Eyes Closed',
    color: '#3B82F6',
    pulse: 'rgba(59,130,246,0.4)',
    Icon: EyeOff,
  },
};

// Priority order — most severe first
const PRIORITY = [
  'identity_mismatch',
  'multiple_faces_detected',
  'no_face_detected',
  'head_turned_away',
  'gaze_away_from_screen',
  'eyes_closed_extended',
];

export default function VisionStatusBadge({ activeFlags, className = '' }: VisionStatusBadgeProps) {
  const topFlag = PRIORITY.find((f) => activeFlags.includes(f)) ?? null;

  const isClean = !topFlag;
  const info = topFlag ? FLAG_INFO[topFlag] : null;

  const dotColor = isClean ? '#10B981' : info!.color;
  const pulseColor = isClean ? 'rgba(16,185,129,0.4)' : info!.pulse;
  const label = isClean ? 'Clear' : info!.label;
  const Icon = isClean ? ShieldCheck : info!.Icon;

  return (
    <>
      <style>{`
        @keyframes visionPulse {
          0%, 100% { transform: scale(1); opacity: 1; box-shadow: 0 0 0 0 var(--pulse-color); }
          50% { transform: scale(1.15); opacity: 0.85; box-shadow: 0 0 0 5px transparent; }
        }
        .vision-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          animation: visionPulse 1.5s ease-in-out infinite;
          flex-shrink: 0;
        }
      `}</style>

      <div
        className={className}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 7,
          padding: '5px 12px',
          borderRadius: 20,
          background: isClean ? 'rgba(16,185,129,0.1)' : `${dotColor}18`,
          border: `1px solid ${isClean ? 'rgba(16,185,129,0.25)' : `${dotColor}40`}`,
          fontFamily: "'Inter', -apple-system, sans-serif",
          fontSize: 12,
          fontWeight: 600,
          color: dotColor,
          transition: 'all 0.3s ease',
        }}
      >
        <div
          className="vision-dot"
          style={{
            backgroundColor: dotColor,
            // @ts-ignore
            '--pulse-color': pulseColor,
          }}
        />
        <Icon size={12} />
        <span>{label}</span>
        {!isClean && activeFlags.length > 1 && (
          <span style={{
            background: `${dotColor}25`,
            color: dotColor,
            fontSize: 10,
            fontWeight: 700,
            padding: '1px 6px',
            borderRadius: 10,
          }}>
            +{activeFlags.length - 1}
          </span>
        )}
      </div>
    </>
  );
}
