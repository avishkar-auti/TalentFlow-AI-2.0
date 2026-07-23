import React, { useEffect, useState, useCallback } from 'react';
import {
  ShieldCheck, ShieldAlert, Eye, EyeOff, UserX, Users,
  AlertTriangle, Clock, ChevronDown, ChevronUp, RefreshCw
} from 'lucide-react';

// ── Types ────────────────────────────────────────────────────────────────────

interface ProctoringFlag {
  event: string;
  timestamp: string;
  start_timestamp?: string;
  duration_seconds: number;
  details?: Record<string, any>;
}

interface ProctoringData {
  interview_id: string;
  total_flags: number;
  summary: string;
  flags: ProctoringFlag[];
}

interface ProctoringPanelProps {
  candidateId: string;
  interviewId: string;
  interviewerView?: boolean;
}

// ── Flag config ───────────────────────────────────────────────────────────────

const FLAG_CONFIG: Record<string, { label: string; color: string; bgColor: string; borderColor: string; Icon: React.FC<any> }> = {
  gaze_away_from_screen: {
    label: 'Gaze Away From Screen',
    color: '#F59E0B',
    bgColor: 'rgba(245,158,11,0.08)',
    borderColor: 'rgba(245,158,11,0.25)',
    Icon: Eye,
  },
  head_turned_away: {
    label: 'Head Turned Away',
    color: '#F97316',
    bgColor: 'rgba(249,115,22,0.08)',
    borderColor: 'rgba(249,115,22,0.25)',
    Icon: UserX,
  },
  no_face_detected: {
    label: 'No Face Detected',
    color: '#EF4444',
    bgColor: 'rgba(239,68,68,0.08)',
    borderColor: 'rgba(239,68,68,0.25)',
    Icon: UserX,
  },
  multiple_faces_detected: {
    label: 'Multiple Faces Detected',
    color: '#DC2626',
    bgColor: 'rgba(220,38,38,0.08)',
    borderColor: 'rgba(220,38,38,0.25)',
    Icon: Users,
  },
  identity_mismatch: {
    label: 'Identity Mismatch',
    color: '#7C3AED',
    bgColor: 'rgba(124,58,237,0.08)',
    borderColor: 'rgba(124,58,237,0.25)',
    Icon: AlertTriangle,
  },
  eyes_closed_extended: {
    label: 'Eyes Closed (Extended)',
    color: '#3B82F6',
    bgColor: 'rgba(59,130,246,0.08)',
    borderColor: 'rgba(59,130,246,0.25)',
    Icon: EyeOff,
  },
};

const DEFAULT_FLAG = {
  label: 'Integrity Flag',
  color: '#6B7280',
  bgColor: 'rgba(107,114,128,0.08)',
  borderColor: 'rgba(107,114,128,0.25)',
  Icon: ShieldAlert,
};

function getFlagConfig(event: string) {
  return FLAG_CONFIG[event] ?? DEFAULT_FLAG;
}

// ── Severity summary ──────────────────────────────────────────────────────────

const SEVERITY_ORDER = [
  'identity_mismatch',
  'multiple_faces_detected',
  'no_face_detected',
  'head_turned_away',
  'gaze_away_from_screen',
  'eyes_closed_extended',
];

function getHighestSeverity(flags: ProctoringFlag[]): string | null {
  for (const event of SEVERITY_ORDER) {
    if (flags.some((f) => f.event === event)) return event;
  }
  return null;
}

// ── Skeleton loader ───────────────────────────────────────────────────────────

function SkeletonRow() {
  return (
    <div style={{
      display: 'flex', gap: 12, alignItems: 'center',
      padding: '12px 0', borderBottom: '1px solid rgba(255,255,255,0.05)',
      animation: 'pulse 1.8s ease-in-out infinite',
    }}>
      <div style={{ width: 36, height: 36, borderRadius: 8, background: 'rgba(255,255,255,0.08)' }} />
      <div style={{ flex: 1 }}>
        <div style={{ height: 12, width: '55%', borderRadius: 6, background: 'rgba(255,255,255,0.08)', marginBottom: 8 }} />
        <div style={{ height: 10, width: '35%', borderRadius: 6, background: 'rgba(255,255,255,0.06)' }} />
      </div>
      <div style={{ width: 56, height: 24, borderRadius: 12, background: 'rgba(255,255,255,0.08)' }} />
    </div>
  );
}

// ── Flag row ──────────────────────────────────────────────────────────────────

function FlagRow({ flag, expanded }: { flag: ProctoringFlag; expanded: boolean }) {
  const cfg = getFlagConfig(flag.event);
  const { Icon } = cfg;

  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 12,
      padding: '12px 14px',
      background: cfg.bgColor,
      border: `1px solid ${cfg.borderColor}`,
      borderRadius: 10,
      marginBottom: 8,
      transition: 'all 0.2s ease',
      animation: 'fadeSlideIn 0.35s ease both',
    }}>
      <div style={{
        width: 36, height: 36, borderRadius: 8,
        background: cfg.bgColor,
        border: `1px solid ${cfg.borderColor}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexShrink: 0,
      }}>
        <Icon size={16} color={cfg.color} />
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: cfg.color, marginBottom: 3 }}>
          {cfg.label}
        </div>
        {expanded && (
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.45)', display: 'flex', gap: 12 }}>
            {flag.start_timestamp && (
              <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <Clock size={10} /> {flag.start_timestamp}
              </span>
            )}
            {flag.details && Object.keys(flag.details).length > 0 && (
              <span>{JSON.stringify(flag.details)}</span>
            )}
          </div>
        )}
      </div>

      <div style={{
        padding: '3px 10px', borderRadius: 20,
        background: cfg.bgColor,
        border: `1px solid ${cfg.borderColor}`,
        fontSize: 11, fontWeight: 700, color: cfg.color,
        whiteSpace: 'nowrap',
      }}>
        {flag.duration_seconds}s
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export default function ProctoringPanel({
  candidateId,
  interviewId,
  interviewerView = true,
}: ProctoringPanelProps) {
  const [data, setData] = useState<ProctoringData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(true);
  const [detailExpanded, setDetailExpanded] = useState(true);

  const fetchFlags = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `/api/v1/candidates/${candidateId}/interview/${interviewId}/proctoring-flags`
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json.data ?? json);
    } catch (err: any) {
      setError(err.message ?? 'Failed to load proctoring data');
    } finally {
      setLoading(false);
    }
  }, [candidateId, interviewId]);

  useEffect(() => { fetchFlags(); }, [fetchFlags]);

  const highestSeverity = data ? getHighestSeverity(data.flags) : null;
  const severityColor = highestSeverity ? getFlagConfig(highestSeverity).color : '#10B981';

  return (
    <>
      <style>{`
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(6px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.45; }
        }
      `}</style>

      <div style={{
        background: 'rgba(15,17,27,0.85)',
        backdropFilter: 'blur(16px)',
        border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: 16,
        overflow: 'hidden',
        fontFamily: "'Inter', -apple-system, sans-serif",
      }}>
        {/* Header */}
        <div
          onClick={() => setExpanded(!expanded)}
          style={{
            display: 'flex', alignItems: 'center', gap: 10,
            padding: '14px 18px',
            borderBottom: expanded ? '1px solid rgba(255,255,255,0.07)' : 'none',
            cursor: 'pointer',
            userSelect: 'none',
            background: 'rgba(255,255,255,0.02)',
          }}
        >
          <ShieldCheck size={16} color={severityColor} />
          <span style={{ flex: 1, fontSize: 13, fontWeight: 600, color: '#E2E8F0' }}>
            Integrity Report
          </span>

          {data && (
            <span style={{
              padding: '2px 10px', borderRadius: 20,
              background: data.total_flags === 0
                ? 'rgba(16,185,129,0.12)' : 'rgba(239,68,68,0.12)',
              color: data.total_flags === 0 ? '#10B981' : '#EF4444',
              fontSize: 11, fontWeight: 700,
            }}>
              {data.total_flags === 0 ? 'Clear' : `${data.total_flags} flag${data.total_flags !== 1 ? 's' : ''}`}
            </span>
          )}

          <button
            onClick={(e) => { e.stopPropagation(); fetchFlags(); }}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: 'rgba(255,255,255,0.35)', padding: 4, borderRadius: 6,
              display: 'flex', alignItems: 'center',
            }}
            title="Refresh"
          >
            <RefreshCw size={13} />
          </button>

          {expanded ? (
            <ChevronUp size={14} color="rgba(255,255,255,0.35)" />
          ) : (
            <ChevronDown size={14} color="rgba(255,255,255,0.35)" />
          )}
        </div>

        {/* Body */}
        {expanded && (
          <div style={{ padding: '14px 18px' }}>
            {loading ? (
              <>
                <SkeletonRow />
                <SkeletonRow />
                <SkeletonRow />
              </>
            ) : error ? (
              <div style={{
                textAlign: 'center', padding: '20px 0',
                color: 'rgba(255,255,255,0.35)', fontSize: 12,
              }}>
                <ShieldAlert size={28} color="#6B7280" style={{ marginBottom: 8, display: 'block', margin: '0 auto 8px' }} />
                {error}
              </div>
            ) : data?.total_flags === 0 ? (
              /* Clean state */
              <div style={{
                textAlign: 'center', padding: '20px 0',
                animation: 'fadeSlideIn 0.4s ease both',
              }}>
                <div style={{
                  width: 48, height: 48, borderRadius: 24,
                  background: 'rgba(16,185,129,0.1)',
                  border: '1px solid rgba(16,185,129,0.25)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 12px',
                }}>
                  <ShieldCheck size={22} color="#10B981" />
                </div>
                <div style={{ fontSize: 13, fontWeight: 600, color: '#10B981', marginBottom: 4 }}>
                  No Integrity Flags Detected
                </div>
                <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.35)' }}>
                  Session completed without proctoring violations
                </div>
              </div>
            ) : (
              /* Flag list */
              <div>
                {interviewerView && (
                  <div style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    marginBottom: 12,
                  }}>
                    <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.45)' }}>
                      {data!.summary}
                    </span>
                    <button
                      onClick={() => setDetailExpanded(!detailExpanded)}
                      style={{
                        background: 'none', border: 'none', cursor: 'pointer',
                        fontSize: 11, color: 'rgba(255,255,255,0.4)',
                        display: 'flex', alignItems: 'center', gap: 4,
                      }}
                    >
                      {detailExpanded ? 'Hide details' : 'Show details'}
                      {detailExpanded ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
                    </button>
                  </div>
                )}

                {data!.flags.map((flag, idx) => (
                  <FlagRow key={idx} flag={flag} expanded={detailExpanded} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}
