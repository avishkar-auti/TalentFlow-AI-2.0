import React, { useState, useEffect, useRef } from 'react';
import { Calendar, Video, Clock, CheckCircle2, XCircle, Search, RefreshCw, Copy, ExternalLink, MessageSquare, Plus, Users, Briefcase, X, Send, AlertCircle, Loader2, Pencil, Trash2 } from 'lucide-react';
import { apiClient } from '../utils/api';

const ROUNDS = ['All', 'AI Screening', 'HR Round', 'Technical Coding'];

// Map UI-friendly round labels <-> backend `type` values expected by the Interview model.
const ROUND_LABEL_TO_TYPE: Record<string, string> = {
  'AI Screening': 'ai_screening',
  'HR Round': 'hr_round',
  'Technical Coding': 'technical_coding',
};
const ROUND_TYPE_TO_LABEL: Record<string, string> = {
  ai_screening: 'AI Screening',
  hr_round: 'HR Round',
  technical_coding: 'Technical Coding',
};
const getRoundLabel = (interview: any) =>
  ROUND_TYPE_TO_LABEL[interview.type || interview.interview_round] || interview.round_type || interview.type || 'AI Screening';

export default function Interviews() {
  const [interviews, setInterviews] = useState<any[]>([]);
  const [candidates, setCandidates] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [activeTab, setActiveTab] = useState('All');
  const [copiedLink, setCopiedLink] = useState('');
  
  // Modals
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [showChatPanel, setShowChatPanel] = useState<string | null>(null);

  // Schedule Form
  const [newCandidateId, setNewCandidateId] = useState('');
  const [newJobId, setNewJobId] = useState('');
  const [newRoundType, setNewRoundType] = useState('AI Screening');
  const [newTime, setNewTime] = useState('');
  const [newDuration, setNewDuration] = useState(45);
  const [scheduleError, setScheduleError] = useState('');
  const [isScheduling, setIsScheduling] = useState(false);

  // Edit Modal
  const [editingInterview, setEditingInterview] = useState<any>(null);
  const [editRoundType, setEditRoundType] = useState('AI Screening');
  const [editTime, setEditTime] = useState('');
  const [editError, setEditError] = useState('');
  const [isSavingEdit, setIsSavingEdit] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Chat
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [chatInput, setChatInput] = useState('');
  const wsRef = useRef<WebSocket | null>(null);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [intRes, candRes, jobsRes] = await Promise.all([
        apiClient.get('/interviews').catch(() => null),
        apiClient.get('/candidates').catch(() => null),
        apiClient.get('/jobs').catch(() => null)
      ]);

      let intData = intRes?.data?.data || intRes?.data || [];
      if (!intData.length) {
        intData = [
          { id: 'INT-1', candidate_id: 'C-101', job_id: 'JOB-20260724-ABC123', round_type: 'Technical Coding', status: 'Scheduled', scheduled_time: new Date(Date.now() + 3600000).toISOString(), meet_link: 'http://localhost:5173/interview/INT-1' },
          { id: 'INT-2', candidate_id: 'C-102', job_id: 'JOB-20260724-ABC123', round_type: 'AI Screening', status: 'Completed', scheduled_time: new Date(Date.now() - 86400000).toISOString(), meet_link: 'http://localhost:5173/interview/INT-2' },
          { id: 'INT-3', candidate_id: 'C-103', job_id: 'JOB-20260724-XYZ789', round_type: 'HR Round', status: 'In Progress', scheduled_time: new Date().toISOString(), meet_link: 'http://localhost:5173/interview/INT-3' }
        ];
      }
      // Normalize real backend records (which use `type` / `scheduled_at`) so the
      // existing UI — built around `round_type` / `scheduled_time` — keeps working
      // unchanged, without needing to touch every render line below.
      intData = intData.map((int: any) => ({
        ...int,
        round_type: int.round_type || getRoundLabel(int),
        scheduled_time: int.scheduled_time || int.scheduled_at,
      }));
      setInterviews(intData);

      let candList = candRes?.data?.data || candRes?.data || [
        { id: 'C-101', name: 'Alice Smith', email: 'alice@example.com' },
        { id: 'C-102', name: 'Bob Johnson', email: 'bob@example.com' },
        { id: 'C-103', name: 'Charlie Davis', email: 'charlie@example.com' }
      ];
      setCandidates(candList);

      let jobsList = jobsRes?.data?.data || jobsRes?.data || [
        { id: 'JOB-20260724-ABC123', title: 'Senior React Developer' },
        { id: 'JOB-20260724-XYZ789', title: 'Product Manager' }
      ];
      setJobs(jobsList);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  // Chat WebSocket logic
  useEffect(() => {
    if (showChatPanel) {
      wsRef.current = new WebSocket(`ws://localhost:8000/ws/recruiter-chat/${showChatPanel}?role=recruiter`);
      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          // Server relays live messages as {type:'chat_message', sender_role, content, timestamp}
          // and confirms our own sends as {type:'sent', timestamp} — only render actual messages.
          if (data.type === 'chat_message') {
            setChatMessages(prev => [...prev, { content: data.content, sender_role: data.sender_role, timestamp: data.timestamp }]);
          }
        } catch {
          // ignore malformed frames
        }
      };
      return () => {
        if (wsRef.current) wsRef.current.close();
      };
    }
  }, [showChatPanel]);

  const sendChatMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (chatInput.trim() && wsRef.current) {
      // Backend recruiter-chat relay expects a `content` field.
      wsRef.current.send(JSON.stringify({ content: chatInput }));
      setChatMessages(prev => [...prev, { content: chatInput, sender_role: 'recruiter', timestamp: new Date().toISOString() }]);
      setChatInput('');
    }
  };

  const handleAction = async (id: string, action: 'pass' | 'fail') => {
    try {
      await apiClient.post(`/interviews/${id}/${action}`);
      fetchAll();
    } catch (err) {
      console.error(err);
    }
  };

  const resetScheduleForm = () => {
    setNewCandidateId('');
    setNewJobId('');
    setNewRoundType('AI Screening');
    setNewTime('');
    setNewDuration(45);
    setScheduleError('');
  };

  const handleScheduleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setScheduleError('');

    if (!newCandidateId || !newJobId || !newTime) {
      setScheduleError('Please fill in candidate, job role and date/time.');
      return;
    }

    setIsScheduling(true);
    try {
      // Backend expects `scheduled_at` (ISO string) and `type` (backend enum), not
      // `scheduled_time` / `round_type` — mismatched field names previously caused
      // every schedule request to be rejected with a 422 validation error.
      await apiClient.post('/interviews', {
        candidate_id: newCandidateId,
        job_id: newJobId,
        type: ROUND_LABEL_TO_TYPE[newRoundType] || 'ai_screening',
        scheduled_at: new Date(newTime).toISOString(),
        duration_minutes: newDuration,
      });
      setShowScheduleModal(false);
      resetScheduleForm();
      await fetchAll();
    } catch (err: any) {
      console.error(err);
      const message = err?.response?.data?.detail || err?.response?.data?.message || 'Failed to schedule interview. Please try again.';
      setScheduleError(message);
    } finally {
      setIsScheduling(false);
    }
  };

  const copyLink = (link: string) => {
    navigator.clipboard.writeText(link);
    setCopiedLink(link);
    setTimeout(() => setCopiedLink(''), 2000);
  };

  // Convert an ISO timestamp into the `datetime-local` input format (YYYY-MM-DDTHH:mm) for prefill.
  const toDatetimeLocal = (isoString: string) => {
    if (!isoString) return '';
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return '';
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  };

  const openEditModal = (interview: any) => {
    setEditingInterview(interview);
    setEditRoundType(getRoundLabel(interview));
    setEditTime(toDatetimeLocal(interview.scheduled_time));
    setEditError('');
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingInterview) return;
    setEditError('');

    if (!editTime) {
      setEditError('Please choose a date/time.');
      return;
    }

    setIsSavingEdit(true);
    try {
      await apiClient.put(`/interviews/${editingInterview.id}`, {
        type: ROUND_LABEL_TO_TYPE[editRoundType] || 'ai_screening',
        scheduled_at: new Date(editTime).toISOString(),
      });
      setEditingInterview(null);
      await fetchAll();
    } catch (err: any) {
      console.error(err);
      const message = err?.response?.data?.detail || err?.response?.data?.message || 'Failed to update interview. Please try again.';
      setEditError(message);
    } finally {
      setIsSavingEdit(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Cancel and remove this scheduled interview? This cannot be undone.')) return;
    setDeletingId(id);
    try {
      await apiClient.delete(`/interviews/${id}`);
      await fetchAll();
    } catch (err) {
      console.error(err);
      window.alert('Failed to remove the interview. Please try again.');
    } finally {
      setDeletingId(null);
    }
  };

  const getCandidateName = (id: string) => candidates.find(c => c.id === id)?.name || id;
  const getJobTitle = (id: string) => jobs.find(j => (j.id === id || j.job_id === id))?.title || id;

  const filteredInterviews = interviews.filter(i => activeTab === 'All' || i.round_type === activeTab);

  return (
    <div className="animate-fade-in pb-10 max-w-7xl mx-auto space-y-6 flex h-[calc(100vh-100px)]">
      
      {/* Main Content Area */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${showChatPanel ? 'pr-6 border-r border-gray-200 dark:border-gray-800' : ''}`}>
        
        <div className="flex flex-col md:flex-row md:justify-between md:items-end gap-4 mb-6 shrink-0">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Interviews</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Manage technical and HR rounds, monitor progress.</p>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={fetchAll} className="p-2.5 bg-white dark:bg-navy-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 rounded-xl hover:bg-gray-50 dark:hover:bg-navy-700 transition-colors shadow-sm" title="Refresh">
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button onClick={() => setShowScheduleModal(true)} className="px-5 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-500/25 flex items-center gap-2">
              <Calendar className="w-4 h-4" /> Schedule New
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2 mb-6 shrink-0 overflow-x-auto custom-scrollbar pb-2">
          {ROUNDS.map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)} className={`px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-colors ${activeTab === tab ? 'bg-indigo-600 text-white shadow-md' : 'bg-gray-100 dark:bg-navy-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-navy-700 border border-gray-200 dark:border-gray-700'}`}>
              {tab}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-4">
          {loading ? (
            <div className="text-center py-10 text-gray-500">Loading schedules...</div>
          ) : filteredInterviews.length === 0 ? (
            <div className="text-center py-20 bg-white/30 dark:bg-navy-800/30 rounded-3xl border border-gray-200 dark:border-gray-700 border-dashed">
              <Calendar className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500 dark:text-gray-400 font-medium">No interviews found for {activeTab}.</p>
            </div>
          ) : (
            filteredInterviews.map((int) => (
              <div key={int.id} className="bg-white/80 dark:bg-navy-900/80 backdrop-blur-xl p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow group">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/20 flex flex-col items-center justify-center shrink-0">
                      <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">{new Date(int.scheduled_time).getDate()}</span>
                      <span className="text-[10px] font-semibold text-indigo-500 dark:text-indigo-300 uppercase">{new Date(int.scheduled_time).toLocaleString('default', { month: 'short' })}</span>
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                        {getCandidateName(int.candidate_id)}
                      </h3>
                      <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 mt-1 gap-3">
                        <span className="flex items-center"><Briefcase className="w-3.5 h-3.5 mr-1" /> {getJobTitle(int.job_id)}</span>
                        <span className="flex items-center"><Clock className="w-3.5 h-3.5 mr-1" /> {new Date(int.scheduled_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col items-end gap-2">
                    <div className="flex items-center gap-2">
                      <span className={`px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-md border ${int.round_type === 'Technical Coding' ? 'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-500/10 dark:text-purple-400 dark:border-purple-500/20' : 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-500/10 dark:text-blue-400 dark:border-blue-500/20'}`}>
                        {int.round_type}
                      </span>
                      <span className={`px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-md border ${int.status === 'Completed' ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20' : int.status === 'In Progress' ? 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20' : 'bg-gray-100 text-gray-700 border-gray-200 dark:bg-navy-800 dark:text-gray-300 dark:border-gray-600'}`}>
                        {int.status}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-gray-100 dark:border-gray-800">
                  
                  <div className="flex items-center gap-2">
                    <div className="flex items-center bg-gray-50 dark:bg-navy-950 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                      <span className="px-3 py-1.5 text-xs text-gray-500 font-mono truncate max-w-[150px]">{int.meet_link || 'http://localhost:5173/meet'}</span>
                      <button onClick={() => copyLink(int.meet_link)} className="p-1.5 hover:bg-gray-200 dark:hover:bg-navy-800 text-gray-500 transition-colors border-l border-gray-200 dark:border-gray-700" title="Copy Link">
                        {copiedLink === int.meet_link ? <CheckCircle2 className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </div>
                    <a href={`${int.meet_link}${int.meet_link?.includes('?') ? '&' : '?'}mode=${ROUND_LABEL_TO_TYPE[getRoundLabel(int)] || 'ai_screening'}&role=recruiter`} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 px-4 py-1.5 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 dark:bg-indigo-500/10 dark:text-indigo-400 dark:hover:bg-indigo-500/20 rounded-lg text-sm font-semibold transition-colors border border-indigo-100 dark:border-indigo-500/20">
                      <Video className="w-4 h-4" /> Join Room
                    </a>
                  </div>

                  <div className="flex items-center gap-2">
                    {int.round_type === 'Technical Coding' && (
                      <button onClick={() => setShowChatPanel(showChatPanel === int.id ? null : int.id)} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold transition-colors border ${showChatPanel === int.id ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white dark:bg-navy-900 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-navy-800'}`}>
                        <MessageSquare className="w-4 h-4" /> Chat
                      </button>
                    )}

                    {int.status !== 'Completed' && (
                      <button onClick={() => openEditModal(int)} className="flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-navy-900 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-navy-800 rounded-lg text-sm font-semibold transition-colors" title="Edit / Reschedule">
                        <Pencil className="w-4 h-4" /> Edit
                      </button>
                    )}

                    <button onClick={() => handleDelete(int.id)} disabled={deletingId === int.id} className="flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-navy-900 text-rose-600 dark:text-rose-400 border border-gray-200 dark:border-gray-700 hover:bg-rose-50 dark:hover:bg-rose-500/10 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50" title="Remove Meeting">
                      {deletingId === int.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />} Remove
                    </button>

                    {(int.status === 'Completed' || int.status === 'In Progress') && (
                      <>
                        <button onClick={() => handleAction(int.id, 'pass')} className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-500/10 dark:text-emerald-400 dark:hover:bg-emerald-500/20 rounded-lg text-sm font-semibold transition-colors border border-emerald-100 dark:border-emerald-500/20">
                          <CheckCircle2 className="w-4 h-4" /> Pass
                        </button>
                        <button onClick={() => handleAction(int.id, 'fail')} className="flex items-center gap-1.5 px-3 py-1.5 bg-rose-50 text-rose-700 hover:bg-rose-100 dark:bg-rose-500/10 dark:text-rose-400 dark:hover:bg-rose-500/20 rounded-lg text-sm font-semibold transition-colors border border-rose-100 dark:border-rose-500/20">
                          <XCircle className="w-4 h-4" /> Fail
                        </button>
                        {int.status === 'Completed' && (
                          <button className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 text-gray-700 hover:bg-gray-100 dark:bg-navy-800 dark:text-gray-300 dark:hover:bg-navy-700 rounded-lg text-sm font-semibold transition-colors border border-gray-200 dark:border-gray-700">
                            <ExternalLink className="w-4 h-4" /> Proctoring
                          </button>
                        )}
                      </>
                    )}
                  </div>

                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Chat Side Panel */}
      {showChatPanel && (
        <div className="w-80 shrink-0 flex flex-col bg-white dark:bg-navy-900 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-xl overflow-hidden animate-slide-in-right">
          <div className="p-4 border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-navy-800/50 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-indigo-500" />
              <h3 className="font-bold text-gray-900 dark:text-white text-sm">Live Chat</h3>
            </div>
            <button onClick={() => setShowChatPanel(null)} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"><X className="w-4 h-4" /></button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar bg-gray-50/30 dark:bg-navy-950/30">
            {chatMessages.length === 0 ? (
              <p className="text-center text-xs text-gray-400 mt-10">No messages yet.</p>
            ) : (
              chatMessages.map((m, i) => (
                <div key={i} className={`flex flex-col ${m.sender_role === 'recruiter' ? 'items-end' : 'items-start'}`}>
                  <span className="text-[10px] text-gray-400 mb-1 px-1">{m.sender_role === 'recruiter' ? 'You' : 'Candidate'}</span>
                  <div className={`px-3 py-2 rounded-2xl max-w-[85%] text-sm ${m.sender_role === 'recruiter' ? 'bg-indigo-600 text-white rounded-tr-sm' : 'bg-white dark:bg-navy-800 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-700 rounded-tl-sm'}`}>
                    {m.content}
                  </div>
                </div>
              ))
            )}
          </div>
          <form onSubmit={sendChatMessage} className="p-3 border-t border-gray-100 dark:border-gray-800 bg-white dark:bg-navy-900 flex gap-2">
            <input type="text" value={chatInput} onChange={e=>setChatInput(e.target.value)} placeholder="Type a message..." className="flex-1 px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-navy-950 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 text-gray-900 dark:text-white" />
            <button type="submit" disabled={!chatInput.trim()} className="p-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}

      {/* Schedule Modal */}
      {showScheduleModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-navy-900 rounded-3xl w-full max-w-md shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden animate-fade-in">
            <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center bg-gray-50/50 dark:bg-navy-800/50">
              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Schedule Interview</h3>
                <p className="text-xs text-gray-500">Set up a new meeting</p>
              </div>
              <button onClick={() => setShowScheduleModal(false)} className="p-2 hover:bg-gray-100 dark:hover:bg-navy-800 rounded-full text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"><X className="w-5 h-5" /></button>
            </div>
            
            <form onSubmit={handleScheduleSubmit} className="p-6 space-y-5">
              {scheduleError && (
                <div className="flex items-start gap-2 px-4 py-3 rounded-xl bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 text-rose-700 dark:text-rose-400 text-sm">
                  <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                  <span>{scheduleError}</span>
                </div>
              )}
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Candidate</label>
                <div className="relative">
                  <Users className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <select required value={newCandidateId} onChange={e=>setNewCandidateId(e.target.value)} style={{ colorScheme: 'light', backgroundColor: '#fff', color: '#111827' }} className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 text-sm focus:ring-2 focus:ring-indigo-500 outline-none appearance-none cursor-pointer">
                    <option value="" style={{ backgroundColor: '#fff', color: '#111827' }}>Select Candidate...</option>
                    {candidates.map(c => <option key={c.id} value={c.id} style={{ backgroundColor: '#fff', color: '#111827' }}>{c.name} ({c.email})</option>)}
                  </select>
                </div>
              </div>
              
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Job Role</label>
                <div className="relative">
                  <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <select required value={newJobId} onChange={e=>setNewJobId(e.target.value)} style={{ colorScheme: 'light', backgroundColor: '#fff', color: '#111827' }} className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 text-sm focus:ring-2 focus:ring-indigo-500 outline-none appearance-none cursor-pointer">
                    <option value="" style={{ backgroundColor: '#fff', color: '#111827' }}>Select Job...</option>
                    {jobs.map(j => <option key={j.id||j.job_id} value={j.id||j.job_id} style={{ backgroundColor: '#fff', color: '#111827' }}>{j.title}</option>)}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Round Type</label>
                  <select required value={newRoundType} onChange={e=>setNewRoundType(e.target.value)} style={{ colorScheme: 'light', backgroundColor: '#fff', color: '#111827' }} className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 text-sm focus:ring-2 focus:ring-indigo-500 outline-none appearance-none cursor-pointer">
                    {ROUNDS.filter(r=>r!=='All').map(r => <option key={r} value={r} style={{ backgroundColor: '#fff', color: '#111827' }}>{r}</option>)}
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Date & Time</label>
                  <input required type="datetime-local" value={newTime} onChange={e=>setNewTime(e.target.value)} className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
                </div>
              </div>

              <div className="pt-4 flex justify-end gap-3 border-t border-gray-100 dark:border-gray-800">
                <button type="button" onClick={() => { setShowScheduleModal(false); setScheduleError(''); }} className="px-5 py-2.5 text-sm font-semibold text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-navy-800 rounded-xl transition-colors">Cancel</button>
                <button type="submit" disabled={isScheduling} className="px-6 py-2.5 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 disabled:cursor-not-allowed rounded-xl shadow-lg shadow-indigo-500/25 transition-all flex items-center gap-2">
                  {isScheduling && <Loader2 className="w-4 h-4 animate-spin" />}
                  {isScheduling ? 'Scheduling...' : 'Schedule'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit / Reschedule Modal */}
      {editingInterview && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-navy-900 rounded-3xl w-full max-w-md shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden animate-fade-in">
            <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center bg-gray-50/50 dark:bg-navy-800/50">
              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Edit Interview</h3>
                <p className="text-xs text-gray-500">{getCandidateName(editingInterview.candidate_id)} &middot; {getJobTitle(editingInterview.job_id)}</p>
              </div>
              <button onClick={() => setEditingInterview(null)} className="p-2 hover:bg-gray-100 dark:hover:bg-navy-800 rounded-full text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"><X className="w-5 h-5" /></button>
            </div>

            <form onSubmit={handleEditSubmit} className="p-6 space-y-5">
              {editError && (
                <div className="flex items-start gap-2 px-4 py-3 rounded-xl bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 text-rose-700 dark:text-rose-400 text-sm">
                  <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                  <span>{editError}</span>
                </div>
              )}

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Round Type</label>
                <select required value={editRoundType} onChange={e=>setEditRoundType(e.target.value)} style={{ colorScheme: 'light', backgroundColor: '#fff', color: '#111827' }} className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 text-sm focus:ring-2 focus:ring-indigo-500 outline-none appearance-none cursor-pointer">
                  {ROUNDS.filter(r=>r!=='All').map(r => <option key={r} value={r} style={{ backgroundColor: '#fff', color: '#111827' }}>{r}</option>)}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Date & Time</label>
                <input required type="datetime-local" value={editTime} onChange={e=>setEditTime(e.target.value)} className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
              </div>

              <div className="pt-4 flex justify-end gap-3 border-t border-gray-100 dark:border-gray-800">
                <button type="button" onClick={() => setEditingInterview(null)} className="px-5 py-2.5 text-sm font-semibold text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-navy-800 rounded-xl transition-colors">Cancel</button>
                <button type="submit" disabled={isSavingEdit} className="px-6 py-2.5 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 disabled:cursor-not-allowed rounded-xl shadow-lg shadow-indigo-500/25 transition-all flex items-center gap-2">
                  {isSavingEdit && <Loader2 className="w-4 h-4 animate-spin" />}
                  {isSavingEdit ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
