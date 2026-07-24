import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Mail, MapPin, Briefcase, ArrowLeft, RefreshCw, Upload,
  CheckCircle, AlertTriangle, ShieldCheck, ChevronRight,
  FileText, BarChart2, Mic, Code, Star, Clock
} from 'lucide-react';
import { apiClient } from '../utils/api';
import ProctoringPanel from '../components/ProctoringPanel';

// ── Stage config ──────────────────────────────────────────────────────────────
const STAGE_COLORS: Record<string, string> = {
  applied:     'bg-gray-500/10 text-gray-400',
  screening:   'bg-blue-500/10 text-blue-400',
  interview:   'bg-violet-500/10 text-violet-400',
  technical:   'bg-amber-500/10 text-amber-400',
  decision:    'bg-orange-500/10 text-orange-400',
  offer:       'bg-emerald-500/10 text-emerald-400',
  rejected:    'bg-red-500/10 text-red-400',
  deleted:     'bg-gray-500/10 text-gray-300',
};

const PIPELINE_STAGES = ['applied','screening','shortlisted','interview','technical','decision','offer'];

// ── Score ring ────────────────────────────────────────────────────────────────
function ScoreRing({ score }: { score: number | null }) {
  const pct = score ?? 0;
  const color = pct >= 80 ? '#10B981' : pct >= 60 ? '#F59E0B' : '#EF4444';
  const r = 36, circ = 2 * Math.PI * r;
  const fill = (pct / 100) * circ;
  return (
    <div className="flex flex-col items-center">
      <svg width="88" height="88" viewBox="0 0 88 88">
        <circle cx="44" cy="44" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
        <circle cx="44" cy="44" r={r} fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={`${fill} ${circ - fill}`}
          strokeDashoffset={circ / 4}
          strokeLinecap="round" style={{ transition: 'stroke-dasharray 0.6s ease' }} />
        <text x="44" y="50" textAnchor="middle" fill={color} fontSize="18" fontWeight="700">
          {score !== null ? `${Math.round(pct)}` : '—'}
        </text>
      </svg>
      <span className="text-xs text-gray-400 mt-1">AI Match Score</span>
    </div>
  );
}

// ── Skeleton loader ───────────────────────────────────────────────────────────
function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded-lg bg-gray-200 dark:bg-navy-700/60 ${className}`} />;
}

// ── Main Component ────────────────────────────────────────────────────────────
export default function CandidateProfile() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');

  // Data states
  const [candidate, setCandidate] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);
  const [resumeAnalysis, setResumeAnalysis] = useState<any>(null);
  const [matching, setMatching] = useState<any>(null);
  const [decision, setDecision] = useState<any>(null);
  const [interviews, setInterviews] = useState<any[]>([]);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [moving, setMoving] = useState(false);
  const [uploadMsg, setUploadMsg] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const [candRes, sumRes, resumeRes, matchRes, decRes, intRes, timeRes] = await Promise.allSettled([
        apiClient.get(`/candidates/${id}`),
        apiClient.get(`/candidates/${id}/summary`),
        apiClient.get(`/candidates/${id}/resume-analysis`),
        apiClient.get(`/candidates/${id}/matching`),
        apiClient.get(`/candidates/${id}/decision`),
        apiClient.get(`/interviews?candidate_id=${id}`),
        apiClient.get(`/candidates/${id}/timeline`),
      ]);

      if (candRes.status === 'fulfilled') setCandidate(candRes.value.data?.data || null);
      if (sumRes.status === 'fulfilled') setSummary(sumRes.value.data?.data || null);
      if (resumeRes.status === 'fulfilled') setResumeAnalysis(resumeRes.value.data?.data || null);
      if (matchRes.status === 'fulfilled') setMatching(matchRes.value.data?.data || null);
      if (decRes.status === 'fulfilled') setDecision(decRes.value.data?.data || null);
      if (intRes.status === 'fulfilled') {
        const intList = intRes.value.data?.data;
        setInterviews(Array.isArray(intList) ? intList : []);
      }
      if (timeRes.status === 'fulfilled') {
        const timeList = timeRes.value.data?.data;
        setTimeline(Array.isArray(timeList) ? timeList : []);
      }
    } catch (err) {
      console.error('Candidate profile fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleMoveStage = async (stage: string) => {
    if (!id || moving) return;
    setMoving(true);
    try {
      await apiClient.patch(`/candidates/${id}/stage`, { stage });
      await fetchAll();
    } catch (err) {
      console.error('Move stage error:', err);
    } finally {
      setMoving(false);
    }
  };

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !id) return;
    const form = new FormData();
    form.append('file', file);
    try {
      setUploadMsg('Uploading...');
      await apiClient.post(`/candidates/${id}/resume`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setUploadMsg('Resume uploaded — analysis queued');
      setTimeout(() => setUploadMsg(null), 4000);
      await fetchAll();
    } catch (err) {
      setUploadMsg('Upload failed');
      setTimeout(() => setUploadMsg(null), 3000);
    }
  };

  const tabs = ['overview', 'resume', 'matching', 'interviews', 'technical', 'decision', 'timeline'];

  const stageColor = STAGE_COLORS[candidate?.pipeline_stage || 'applied'] || 'bg-gray-500/10 text-gray-400';
  const avatarLetter = candidate?.name?.charAt(0)?.toUpperCase() || id?.charAt(0)?.toUpperCase() || 'C';
  const avatarBg = `hsl(${(candidate?.name?.charCodeAt(0) || 200) * 17 % 360}, 65%, 50%)`;

  return (
    <div className="animate-fade-in pb-20">
      {/* Back */}
      <button
        onClick={() => navigate(-1)}
        className="inline-flex items-center text-sm text-gray-500 dark:text-gray-400 hover:text-blue-500 mb-6 transition"
      >
        <ArrowLeft className="w-4 h-4 mr-1" /> Back
      </button>

      {/* Header Card */}
      <div className="glass-card p-6 mb-6">
        <div className="flex flex-col md:flex-row justify-between md:items-start gap-4">
          <div className="flex items-center gap-5">
            {/* Dynamic avatar */}
            <div className="w-20 h-20 rounded-full flex items-center justify-center text-white text-3xl font-bold shadow-lg flex-shrink-0"
              style={{ background: `linear-gradient(135deg, ${avatarBg}, hsl(${(candidate?.name?.charCodeAt(0) || 200) * 17 % 360}, 45%, 35%))` }}>
              {avatarLetter}
            </div>
            <div>
              {loading ? (
                <>
                  <Skeleton className="h-7 w-48 mb-2" />
                  <Skeleton className="h-4 w-36 mb-2" />
                  <Skeleton className="h-4 w-52" />
                </>
              ) : (
                <>
                  <h1 className="text-2xl font-bold dark:text-white">{candidate?.name || id}</h1>
                  <p className="text-gray-500 dark:text-gray-400 text-sm mt-1 flex items-center gap-1">
                    <Briefcase className="w-3.5 h-3.5" />
                    {candidate?.job_id ? `Job: ${candidate.job_id}` : 'No job linked'}
                  </p>
                  <div className="flex gap-4 mt-2 text-xs text-gray-500 flex-wrap">
                    {candidate?.email && (
                      <span className="flex items-center gap-1"><Mail className="w-3 h-3" />{candidate.email}</span>
                    )}
                    {candidate?.location && (
                      <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{candidate.location}</span>
                    )}
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold capitalize ${stageColor}`}>
                      {candidate?.pipeline_stage || 'applied'}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex flex-col gap-2 items-end">
            <div className="flex gap-2 flex-wrap justify-end">
              <button
                onClick={() => handleMoveStage('shortlisted')}
                disabled={moving || loading || candidate?.pipeline_stage === 'shortlisted'}
                className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-semibold hover:bg-emerald-700 transition shadow-lg shadow-emerald-600/25 disabled:opacity-50 flex items-center gap-1"
              >
                Shortlist Candidate 🌟
              </button>
              <button
                onClick={() => handleMoveStage('rejected')}
                disabled={moving || loading}
                className="px-4 py-2 bg-gray-100 dark:bg-navy-800 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-500 transition disabled:opacity-50"
              >
                Reject
              </button>
              <button
                onClick={() => {
                  const current = PIPELINE_STAGES.indexOf(candidate?.pipeline_stage || 'applied');
                  const next = PIPELINE_STAGES[current + 1];
                  if (next) handleMoveStage(next);
                }}
                disabled={moving || loading || candidate?.pipeline_stage === 'offer'}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition shadow-lg shadow-blue-600/25 disabled:opacity-50 flex items-center gap-1"
              >
                {moving ? 'Moving...' : 'Move to Next Stage'} <ChevronRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => {
                  const salary = prompt('Enter salary (e.g., $120,000):');
                  const startDate = prompt('Enter start date (YYYY-MM-DD):');
                  if (salary && startDate) {
                    apiClient.post('/interviews/offer/generate', {
                      candidate_id: candidate?.id,
                      job_id: candidate?.job_id,
                      salary,
                      start_date: startDate
                    }).then(() => {
                      alert('Offer sent!');
                      handleMoveStage('offer');
                    }).catch(e => alert('Error: ' + e.message));
                  }
                }}
                disabled={loading}
                className="px-4 py-2 bg-amber-600 text-white rounded-lg text-sm font-medium hover:bg-amber-700 transition shadow-lg shadow-amber-600/25 disabled:opacity-50 flex items-center gap-1"
              >
                📧 Send Offer Letter
              </button>
            </div>
            <label className="flex items-center gap-1 text-xs text-blue-400 cursor-pointer hover:text-blue-300 transition">
              <Upload className="w-3.5 h-3.5" />
              {uploadMsg || 'Upload Resume'}
              <input type="file" accept=".pdf" className="hidden" onChange={handleResumeUpload} />
            </label>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-6 mt-8 border-b border-gray-200 dark:border-gray-800 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 text-sm font-medium capitalize transition-colors relative whitespace-nowrap ${
                activeTab === tab ? 'text-blue-500' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              {tab}
              {activeTab === tab && <span className="absolute bottom-0 left-0 w-full h-0.5 bg-blue-500 rounded-t-full" />}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">

          {/* ── OVERVIEW ── */}
          {activeTab === 'overview' && (
            <>
              {/* AI Summary */}
              <div className="glass-card p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Star className="w-5 h-5 text-amber-400" />
                  <h3 className="text-lg font-bold dark:text-white">AI Decision Summary</h3>
                </div>
                {loading ? (
                  <div className="space-y-3">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-4/5" />
                    <Skeleton className="h-4 w-2/3" />
                  </div>
                ) : !summary || summary.status === 'not_found' ? (
                  <p className="text-sm text-gray-400 italic">No AI analysis available yet. Process the resume to generate a summary.</p>
                ) : (
                  <div className="space-y-4">
                    {summary.recommendation && (
                      <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-semibold ${
                        summary.recommendation === 'RECOMMENDED'
                          ? 'bg-emerald-500/10 text-emerald-400'
                          : summary.recommendation === 'MAYBE'
                          ? 'bg-amber-500/10 text-amber-400'
                          : 'bg-red-500/10 text-red-400'
                      }`}>
                        <ShieldCheck className="w-4 h-4" />
                        {summary.recommendation}
                      </div>
                    )}
                    {summary.remarks && (
                      <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{summary.remarks}</p>
                    )}
                    {Array.isArray(summary.strengths) && summary.strengths.length > 0 && (
                      <div>
                        <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Strengths</p>
                        <ul className="space-y-1.5">
                          {summary.strengths.map((s: string, i: number) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                              <CheckCircle className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />{s}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {Array.isArray(summary.concerns) && summary.concerns.length > 0 && (
                      <div>
                        <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Concerns</p>
                        <ul className="space-y-1.5">
                          {summary.concerns.map((c: string, i: number) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                              <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />{c}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Skills from resume */}
              {(Array.isArray(resumeAnalysis?.skills) || Array.isArray(candidate?.skills)) && (
                <div className="glass-card p-6">
                  <h3 className="text-lg font-bold dark:text-white mb-4">Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {(resumeAnalysis?.skills || candidate?.skills || []).map((skill: string, i: number) => (
                      <span key={i} className="px-3 py-1 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-300 text-xs font-medium rounded-full">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Experience from resume analysis */}
              {Array.isArray(resumeAnalysis?.experience) && resumeAnalysis.experience.length > 0 && (
                <div className="glass-card p-6">
                  <h3 className="text-lg font-bold dark:text-white mb-4">Experience</h3>
                  <div className="space-y-6 border-l-2 border-gray-200 dark:border-gray-800 ml-3 pl-5 relative">
                    {resumeAnalysis.experience.map((exp: any, i: number) => (
                      <div key={i} className="relative">
                        <div className="absolute -left-[27px] top-1 w-3 h-3 rounded-full bg-blue-500 ring-4 ring-white dark:ring-navy-900" />
                        <h4 className="font-semibold text-gray-900 dark:text-white">{exp.title || exp.role}</h4>
                        <p className="text-sm text-blue-500 mb-1">{exp.company}{exp.duration ? ` • ${exp.duration}` : ''}</p>
                        {exp.description && <p className="text-sm text-gray-600 dark:text-gray-400">{exp.description}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* ── RESUME & ATS BREAKDOWN ── */}
          {activeTab === 'resume' && (
            <div className="space-y-6">
              <div className="glass-card p-6">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-blue-400" />
                    <h3 className="text-lg font-bold dark:text-white">ATS & AST Resume Analysis</h3>
                  </div>
                  <label className="flex items-center gap-1 text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg cursor-pointer transition">
                    <Upload className="w-3.5 h-3.5" /> Re-upload Resume
                    <input type="file" accept=".pdf" className="hidden" onChange={handleResumeUpload} />
                  </label>
                </div>

                {loading ? (
                  <Skeleton className="h-40 w-full" />
                ) : !resumeAnalysis || resumeAnalysis.status === 'not_analyzed' ? (
                  <div className="text-center py-10">
                    <FileText className="w-12 h-12 mx-auto text-gray-400 mb-3" />
                    <p className="text-sm text-gray-400 mb-4">No resume analysis available yet.</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Score Cards Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-gray-50 dark:bg-navy-900/60 p-4 rounded-xl border border-gray-200 dark:border-gray-800 text-center">
                        <span className="text-xs text-gray-500 font-semibold block mb-1">ATS OVERALL SCORE</span>
                        {(() => {
                          const atsScore = resumeAnalysis.score?.ats_score ?? candidate?.atsScore;
                          return atsScore != null ? (
                            <span className={`text-3xl font-extrabold ${atsScore >= 80 ? 'text-emerald-400' : 'text-amber-400'}`}>
                              {Math.round(atsScore)}%
                            </span>
                          ) : (
                            <span className="text-sm text-gray-400 italic">Pending</span>
                          );
                        })()}
                      </div>

                      <div className="bg-gray-50 dark:bg-navy-900/60 p-4 rounded-xl border border-gray-200 dark:border-gray-800 text-center">
                        <span className="text-xs text-gray-500 font-semibold block mb-1">FORMATTING COMPATIBILITY</span>
                        {(() => {
                          const fmtScore = resumeAnalysis.atsFormattingScore ?? candidate?.atsBreakdown?.formatting_quality;
                          return fmtScore != null ? (
                            <span className="text-3xl font-extrabold text-blue-400">{Math.round(fmtScore)}%</span>
                          ) : (
                            <span className="text-sm text-gray-400 italic">Pending</span>
                          );
                        })()}
                      </div>

                      <div className="bg-gray-50 dark:bg-navy-900/60 p-4 rounded-xl border border-gray-200 dark:border-gray-800 text-center">
                        <span className="text-xs text-gray-500 font-semibold block mb-1">PARSED SKILLS COUNT</span>
                        <span className="text-3xl font-extrabold text-violet-400">
                          {(resumeAnalysis.analysis?.skills || candidate?.skills || []).length}
                        </span>
                      </div>
                    </div>

                    {/* Matched Keywords */}
                    <div>
                      <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Matched Job Keywords</h4>
                      <div className="flex flex-wrap gap-2">
                        {(resumeAnalysis.score?.matched_keywords || candidate?.matched_keywords || []).length === 0 ? (
                          <span className="text-xs text-gray-400 italic">No keyword data yet</span>
                        ) : (resumeAnalysis.score?.matched_keywords || candidate?.matched_keywords || []).map((kw: string, i: number) => (
                          <span key={i} className="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold rounded-md uppercase">
                            ✓ {kw}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Missing Keywords */}
                    {(() => {
                      const missing = resumeAnalysis.score?.missing_keywords || candidate?.missing_keywords || [];
                      return Array.isArray(missing) && missing.length > 0 && (
                      <div>
                        <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Top Missing Keywords</h4>
                        <div className="flex flex-wrap gap-2">
                          {missing.map((kw: string, i: number) => (
                            <span key={i} className="px-2.5 py-1 bg-red-500/10 text-red-400 border border-red-500/20 text-xs font-semibold rounded-md uppercase">
                              ✗ {kw}
                            </span>
                          ))}
                        </div>
                      </div>
                      );
                    })()}

                    {/* Formatting Alerts */}
                    {Array.isArray(resumeAnalysis.formattingFlags) && resumeAnalysis.formattingFlags.length > 0 && (
                      <div className="bg-amber-500/10 border border-amber-500/30 p-4 rounded-xl">
                        <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                          <AlertTriangle className="w-4 h-4" /> ATS Formatting Alerts
                        </h4>
                        <ul className="space-y-1">
                          {resumeAnalysis.formattingFlags.map((flag: string, i: number) => (
                            <li key={i} className="text-xs text-amber-300">• {flag}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Raw Text Extract Toggle */}
                    <details className="mt-4">
                      <summary className="text-xs text-gray-500 cursor-pointer hover:text-blue-400 transition">
                        View Extracted AST Raw Text
                      </summary>
                      <pre className="mt-2 text-xs text-gray-400 bg-black/40 p-4 rounded-lg overflow-auto max-h-60">
                        {resumeAnalysis.analysis?.parsedText || JSON.stringify(resumeAnalysis, null, 2)}
                      </pre>
                    </details>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ── MATCHING ── */}
          {activeTab === 'matching' && (
            <div className="glass-card p-6">
              <div className="flex items-center gap-2 mb-4">
                <BarChart2 className="w-5 h-5 text-violet-400" />
                <h3 className="text-lg font-bold dark:text-white">Job Match Scores</h3>
              </div>
              {loading ? <Skeleton className="h-32 w-full" /> :
               !matching || matching.status === 'not_computed' ? (
                <p className="text-sm text-gray-400 italic text-center py-8">Match scores not yet computed.</p>
              ) : (
                <div className="space-y-4">
                  {Object.entries((typeof matching?.scores === 'object' && matching?.scores) || (typeof matching === 'object' && matching) || {}).map(([key, val]: any) => (
                    typeof val === 'number' && (
                      <div key={key}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-600 dark:text-gray-300 capitalize">{key.replace(/_/g, ' ')}</span>
                          <span className="font-bold text-gray-900 dark:text-white">{Math.round(val)}%</span>
                        </div>
                        <div className="h-2 bg-gray-200 dark:bg-navy-700 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all"
                            style={{
                              width: `${Math.min(val, 100)}%`,
                              background: val >= 80 ? '#10B981' : val >= 60 ? '#F59E0B' : '#EF4444'
                            }}
                          />
                        </div>
                      </div>
                    )
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ── INTERVIEWS ── */}
          {activeTab === 'interviews' && (
            <div className="space-y-4">
              {loading ? <Skeleton className="h-24 w-full" /> :
               !Array.isArray(interviews) || interviews.length === 0 ? (
                <div className="glass-card p-8 text-center">
                  <Mic className="w-10 h-10 mx-auto text-gray-300 mb-3" />
                  <p className="text-sm text-gray-400">No interviews scheduled yet.</p>
                </div>
              ) : (
                interviews.map((intv: any) => (
                  <div key={intv.id || intv.interview_id} className="glass-card p-4 space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm font-semibold dark:text-white capitalize">{intv.type || 'AI'} Interview</p>
                        <p className="text-xs text-gray-400 mt-0.5">
                          {intv.scheduled_at ? new Date(intv.scheduled_at).toLocaleString() : 'TBD'}
                        </p>
                      </div>
                      <span className={`px-2.5 py-0.5 text-xs font-semibold rounded-full capitalize ${STAGE_COLORS[intv.status] || 'bg-gray-500/10 text-gray-400'}`}>
                        {intv.status?.replace('_', ' ')}
                      </span>
                    </div>
                    {intv.status === 'completed' && (
                      <ProctoringPanel candidateId={id!} interviewId={intv.id || intv.interview_id} interviewerView={true} />
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {/* ── TECHNICAL CODING SANDBOX ── */}
          {activeTab === 'technical' && (
            <div className="glass-card p-6 space-y-4">
              <div className="flex items-center gap-2 mb-2">
                <Code className="w-5 h-5 text-violet-400" />
                <h3 className="text-lg font-bold dark:text-white">Technical Coding Test Sandbox Submission</h3>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
                Candidate code execution, test pass results, and stdout terminal output.
              </p>
              
              <div className="bg-gray-50 dark:bg-navy-900/50 p-4 rounded-xl space-y-3">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-gray-700 dark:text-gray-300">Target Problem: Two Sum</span>
                  <span className="px-2.5 py-0.5 rounded-full font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Pass Rate: 100% (1/1 Tests Passed)
                  </span>
                </div>
                <div>
                  <span className="text-xs font-semibold text-gray-500 uppercase block mb-1">Submitted Solution (Python)</span>
                  <pre className="text-xs text-emerald-300 bg-black/60 p-4 rounded-lg overflow-auto font-mono max-h-60 border border-gray-800">
{`def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []

# Executed Output: [0, 1]`}
                  </pre>
                </div>
              </div>
            </div>
          )}

          {/* ── DECISION ── */}
          {activeTab === 'decision' && (
            <div className="glass-card p-6">
              <div className="flex items-center gap-2 mb-4">
                <Code className="w-5 h-5 text-orange-400" />
                <h3 className="text-lg font-bold dark:text-white">Final Decision</h3>
              </div>
              {loading ? <Skeleton className="h-32 w-full" /> :
               !decision || decision.status === 'not_generated' ? (
                <div className="text-center py-8">
                  <p className="text-sm text-gray-400 italic mb-4">Decision not yet generated.</p>
                  <button
                    onClick={() => apiClient.post(`/candidates/${id}/decision/generate`).then(fetchAll)}
                    className="px-4 py-2 text-sm bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition"
                  >
                    Generate Decision
                  </button>
                </div>
              ) : (
                <pre className="text-xs text-gray-600 dark:text-gray-300 overflow-auto whitespace-pre-wrap bg-gray-50 dark:bg-navy-900/50 p-4 rounded-lg max-h-96">
                  {JSON.stringify(decision, null, 2)}
                </pre>
              )}
            </div>
          )}

          {/* ── TIMELINE ── */}
          {activeTab === 'timeline' && (
            <div className="glass-card p-6">
              <div className="flex items-center gap-2 mb-4">
                <Clock className="w-5 h-5 text-teal-400" />
                <h3 className="text-lg font-bold dark:text-white">Activity Timeline</h3>
              </div>
              {loading ? (
                <div className="space-y-3">
                  {[1,2,3].map(i => <Skeleton key={i} className="h-12 w-full" />)}
                </div>
              ) : !Array.isArray(timeline) || timeline.length === 0 ? (
                <p className="text-sm text-gray-400 italic text-center py-8">No activity logged yet.</p>
              ) : (
                <div className="space-y-4 border-l-2 border-gray-200 dark:border-gray-800 ml-3 pl-5">
                  {timeline.map((act: any, i: number) => (
                    <div key={i} className="relative">
                      <div className="absolute -left-[27px] top-1 w-3 h-3 rounded-full bg-teal-500 ring-4 ring-white dark:ring-navy-900" />
                      <p className="text-sm font-medium dark:text-white">
                        {typeof act?.details === 'object' ? (act.details?.user_facing_status || act.action) : act?.details || act?.action || 'Activity'}
                      </p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {act?.agent_name || 'System'} •{' '}
                        {act?.created_at || act?.timestamp ? new Date(act.created_at || act.timestamp).toLocaleString() : ''}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Score Ring */}
          <div className="glass-card p-6 flex flex-col items-center gap-4">
            <ScoreRing score={summary?.overallScore ?? matching?.overall_score ?? null} />
            {candidate?.pipeline_stage && (
              <div className="w-full">
                <p className="text-xs font-semibold text-gray-500 uppercase mb-2 text-center">Pipeline Stage</p>
                <div className={`text-center px-3 py-1.5 rounded-full text-sm font-semibold capitalize ${stageColor}`}>
                  {candidate.pipeline_stage}
                </div>
              </div>
            )}
            <button
              onClick={fetchAll}
              className="flex items-center gap-1 text-xs text-gray-400 hover:text-blue-400 transition"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Refresh
            </button>
          </div>

          {/* Quick Info */}
          {!loading && candidate && (
            <div className="glass-card p-5 space-y-3">
              <h4 className="text-sm font-semibold dark:text-white">Profile Info</h4>
              {[
                ['Candidate ID', candidate.id],
                ['Status', candidate.status],
                ['Email', candidate.email],
                ['Resume', candidate.resume_status || candidate.resume_url ? '✓ Uploaded' : '—'],
                ['Created', candidate.created_at ? new Date(candidate.created_at).toLocaleDateString() : '—'],
              ].filter(([,v]) => v).map(([label, value]) => (
                <div key={label} className="flex justify-between text-xs">
                  <span className="text-gray-500 dark:text-gray-400">{label}</span>
                  <span className="font-medium text-gray-800 dark:text-gray-200 truncate max-w-[140px]">{value}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
