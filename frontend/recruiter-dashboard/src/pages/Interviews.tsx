import React, { useState, useEffect, useCallback } from 'react';
import { Calendar, Video, ShieldAlert, Clock, Briefcase, Play, FileText, CheckCircle2, X, RefreshCw, AlertCircle, Plus } from 'lucide-react';
import { apiClient } from '../utils/api';
import ProctoringPanel from '../components/ProctoringPanel';

interface Interview {
  id: string;
  candidate_id: string;
  candidateName?: string;
  job_id: string;
  jobTitle?: string;
  scheduled_at: string;
  duration_minutes: number;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  type: string;
  created_at?: string;
}

export default function Interviews() {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'scheduled' | 'completed' | 'in_progress'>('all');
  const [selectedInterview, setSelectedInterview] = useState<Interview | null>(null);
  const [showScheduleModal, setShowScheduleModal] = useState(false);

  // Schedule form state
  const [candidateId, setCandidateId] = useState('');
  const [jobId, setJobId] = useState('');
  const [scheduledTime, setScheduledTime] = useState('');
  const [interviewType, setInterviewType] = useState('speech');
  const [saving, setSaving] = useState(false);

  const fetchInterviews = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get('/interviews');
      setInterviews(res.data?.data || []);
    } catch (err: any) {
      setError('Failed to load interviews from Firestore.');
      console.error('Interviews fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchInterviews(); }, [fetchInterviews]);

  const handleSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!candidateId || !jobId || !scheduledTime) return;
    setSaving(true);
    try {
      await apiClient.post('/interviews', {
        candidate_id: candidateId,
        job_id: jobId,
        scheduled_at: new Date(scheduledTime).toISOString(),
        type: interviewType,
        duration_minutes: 45,
      });
      setShowScheduleModal(false);
      setCandidateId('');
      setJobId('');
      setScheduledTime('');
      await fetchInterviews();
    } catch (err: any) {
      console.error('Schedule interview error:', err);
    } finally {
      setSaving(false);
    }
  };

  const filtered = interviews.filter(i => {
    if (filter === 'all') return true;
    return i.status === filter;
  });

  const statusBadge = (status: string) => {
    const map: Record<string, string> = {
      scheduled: 'bg-blue-500/10 text-blue-400',
      in_progress: 'bg-amber-500/10 text-amber-400',
      completed: 'bg-emerald-500/10 text-emerald-400',
      cancelled: 'bg-red-500/10 text-red-400',
    };
    return map[status] || 'bg-gray-500/10 text-gray-400';
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AI Interview Management</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Live sessions synced from Firestore — eye tracking &amp; proctoring enabled.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchInterviews}
            className="inline-flex items-center px-3 py-2 text-sm text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-navy-800 rounded-lg hover:bg-gray-200 dark:hover:bg-navy-700 transition"
          >
            <RefreshCw className="w-4 h-4 mr-1" /> Refresh
          </button>
          <button
            onClick={() => setShowScheduleModal(true)}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition shadow-sm"
          >
            <Calendar className="w-4 h-4 mr-2" /> Schedule Interview
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex space-x-2 border-b border-gray-200 dark:border-gray-700/50 pb-2">
        {(['all', 'scheduled', 'in_progress', 'completed'] as const).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors capitalize ${
              filter === f
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-navy-800'
            }`}
          >
            {f === 'all' ? `All (${interviews.length})` : f.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <div key={i} className="glass p-5 rounded-xl border border-gray-200/50 dark:border-gray-700/50 animate-pulse h-48 bg-gray-100 dark:bg-navy-800/50" />
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-16 glass-card rounded-xl">
          <AlertCircle className="w-10 h-10 mx-auto text-red-400 mb-3" />
          <p className="text-sm text-red-400 font-medium">{error}</p>
          <button onClick={fetchInterviews} className="mt-3 text-xs text-blue-400 underline">Retry</button>
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 glass-card rounded-xl">
          <Calendar className="w-10 h-10 mx-auto text-gray-400 mb-3" />
          <h3 className="text-sm font-semibold dark:text-white">No interviews found</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Schedule a new interview to get started.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map(interview => (
            <div
              key={interview.id}
              className="glass p-5 rounded-xl border border-gray-200/50 dark:border-gray-700/50 hover:border-blue-500/50 transition-all flex flex-col justify-between shadow-sm"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-full bg-blue-500/10 dark:bg-blue-500/20 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-lg">
                      {interview.candidate_id?.charAt(0)?.toUpperCase() || 'C'}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white text-sm">
                        {interview.candidateName || interview.candidate_id}
                      </h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center mt-0.5">
                        <Briefcase className="w-3 h-3 mr-1" />
                        {interview.jobTitle || interview.job_id || 'N/A'}
                      </p>
                    </div>
                  </div>
                  <span className={`px-2.5 py-0.5 text-xs font-semibold rounded-full capitalize ${statusBadge(interview.status)}`}>
                    {interview.status?.replace('_', ' ')}
                  </span>
                </div>

                <div className="pt-2 border-t border-gray-100 dark:border-gray-800 space-y-1.5 text-xs text-gray-500 dark:text-gray-400">
                  <div className="flex items-center">
                    <Clock className="w-3.5 h-3.5 mr-1.5 text-blue-500" />
                    {interview.scheduled_at
                      ? new Date(interview.scheduled_at).toLocaleString()
                      : 'Not scheduled'}
                    {interview.duration_minutes ? ` (${interview.duration_minutes} min)` : ''}
                  </div>
                  <div className="flex items-center">
                    <Video className="w-3.5 h-3.5 mr-1.5 text-teal-500" />
                    Type: <span className="font-medium ml-1 text-gray-700 dark:text-gray-200 capitalize">{interview.type || 'AI'}</span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between">
                <button
                  onClick={() => setSelectedInterview(interview)}
                  className="inline-flex items-center text-xs font-medium text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400"
                >
                  <FileText className="w-4 h-4 mr-1.5" /> View Details
                </button>
                {interview.status === 'scheduled' && (
                  <button
                    onClick={() => window.open(`http://localhost:3001/interview/${interview.id}`, '_blank')}
                    className="inline-flex items-center px-3 py-1.5 text-xs font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition"
                  >
                    <Play className="w-3.5 h-3.5 mr-1" /> Join Room
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Interview Detail Modal */}
      {selectedInterview && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-fade-in">
          <div className="bg-white dark:bg-navy-800 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-xl border border-gray-200 dark:border-gray-700 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                  {selectedInterview.candidateName || selectedInterview.candidate_id}
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {selectedInterview.jobTitle || selectedInterview.job_id}
                </p>
              </div>
              <button onClick={() => setSelectedInterview(null)} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="bg-gray-50 dark:bg-navy-900/50 p-4 rounded-lg space-y-2 text-xs">
              <div className="flex justify-between items-center">
                <span className="font-semibold text-gray-700 dark:text-gray-300">Status</span>
                <span className={`px-2 py-0.5 font-semibold rounded-full capitalize ${statusBadge(selectedInterview.status)}`}>
                  {selectedInterview.status?.replace('_', ' ')}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500 dark:text-gray-400">Interview ID</span>
                <span className="font-mono text-gray-600 dark:text-gray-300">{selectedInterview.id}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500 dark:text-gray-400">Scheduled</span>
                <span className="text-gray-600 dark:text-gray-300">
                  {selectedInterview.scheduled_at
                    ? new Date(selectedInterview.scheduled_at).toLocaleString()
                    : 'TBD'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500 dark:text-gray-400">Duration</span>
                <span className="text-gray-600 dark:text-gray-300">{selectedInterview.duration_minutes || 45} min</span>
              </div>
            </div>

            {/* Live Proctoring Panel — fetches from Firestore via API */}
            <div>
              <ProctoringPanel
                candidateId={selectedInterview.candidate_id}
                interviewId={selectedInterview.id}
                interviewerView={true}
              />
            </div>

            <div className="pt-2 flex justify-end gap-2">
              {selectedInterview.status === 'scheduled' && (
                <button
                  onClick={() => window.open(`http://localhost:3001/interview/${selectedInterview.id}`, '_blank')}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition"
                >
                  <Play className="w-4 h-4 inline mr-1" /> Join Session
                </button>
              )}
              <button
                onClick={() => setSelectedInterview(null)}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-navy-700 hover:bg-gray-200 dark:hover:bg-navy-600 rounded-lg transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Schedule Modal */}
      {showScheduleModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-fade-in">
          <div className="bg-white dark:bg-navy-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-xl border border-gray-200 dark:border-gray-700">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Schedule AI Interview</h3>
              <button onClick={() => setShowScheduleModal(false)} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSchedule} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Candidate ID <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={candidateId}
                  onChange={e => setCandidateId(e.target.value)}
                  placeholder="e.g. cand_abc12345"
                  required
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-navy-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Job ID <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={jobId}
                  onChange={e => setJobId(e.target.value)}
                  placeholder="e.g. job_xyz98765"
                  required
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-navy-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Interview Type
                </label>
                <select
                  value={interviewType}
                  onChange={e => setInterviewType(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-navy-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                >
                  <option value="speech">Speech (AI Conversational)</option>
                  <option value="technical">Technical (Coding)</option>
                  <option value="combined">Combined</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Scheduled Date &amp; Time <span className="text-red-400">*</span>
                </label>
                <input
                  type="datetime-local"
                  value={scheduledTime}
                  onChange={e => setScheduledTime(e.target.value)}
                  required
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-navy-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  disabled={saving}
                  className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {saving ? 'Scheduling...' : 'Schedule Interview'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowScheduleModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-navy-700 rounded-lg hover:bg-gray-200 transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
