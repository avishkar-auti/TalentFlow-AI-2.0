import React, { useState, useEffect, useRef } from 'react';
import { Calendar, Video, Clock, CheckCircle2, XCircle, Search, RefreshCw, Copy, ExternalLink, MessageSquare, Plus, Users, Briefcase, X, Send } from 'lucide-react';
import { apiClient } from '../utils/api';

const ROUNDS = ['All', 'AI Screening', 'HR Round', 'Technical Coding'];

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
        const data = JSON.parse(event.data);
        setChatMessages(prev => [...prev, data]);
      };
      return () => {
        if (wsRef.current) wsRef.current.close();
      };
    }
  }, [showChatPanel]);

  const sendChatMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (chatInput.trim() && wsRef.current) {
      const msg = { text: chatInput, sender: 'recruiter', timestamp: new Date().toISOString() };
      wsRef.current.send(JSON.stringify(msg));
      setChatMessages(prev => [...prev, msg]);
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

  const handleScheduleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/interviews', {
        candidate_id: newCandidateId,
        job_id: newJobId,
        round_type: newRoundType,
        scheduled_time: newTime,
        status: 'Scheduled'
      });
      setShowScheduleModal(false);
      fetchAll();
    } catch (err) {
      console.error(err);
    }
  };

  const copyLink = (link: string) => {
    navigator.clipboard.writeText(link);
    setCopiedLink(link);
    setTimeout(() => setCopiedLink(''), 2000);
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
                    <a href={int.meet_link} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 px-4 py-1.5 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 dark:bg-indigo-500/10 dark:text-indigo-400 dark:hover:bg-indigo-500/20 rounded-lg text-sm font-semibold transition-colors border border-indigo-100 dark:border-indigo-500/20">
                      <Video className="w-4 h-4" /> Join Room
                    </a>
                  </div>

                  <div className="flex items-center gap-2">
                    {int.round_type === 'Technical Coding' && (
                      <button onClick={() => setShowChatPanel(showChatPanel === int.id ? null : int.id)} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold transition-colors border ${showChatPanel === int.id ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white dark:bg-navy-900 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-navy-800'}`}>
                        <MessageSquare className="w-4 h-4" /> Chat
                      </button>
                    )}

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
                <div key={i} className={`flex flex-col ${m.sender === 'recruiter' ? 'items-end' : 'items-start'}`}>
                  <span className="text-[10px] text-gray-400 mb-1 px-1">{m.sender === 'recruiter' ? 'You' : 'Candidate'}</span>
                  <div className={`px-3 py-2 rounded-2xl max-w-[85%] text-sm ${m.sender === 'recruiter' ? 'bg-indigo-600 text-white rounded-tr-sm' : 'bg-white dark:bg-navy-800 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-700 rounded-tl-sm'}`}>
                    {m.text}
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
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Candidate</label>
                <div className="relative">
                  <Users className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <select required value={newCandidateId} onChange={e=>setNewCandidateId(e.target.value)} className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 outline-none appearance-none cursor-pointer">
                    <option value="">Select Candidate...</option>
                    {candidates.map(c => <option key={c.id} value={c.id}>{c.name} ({c.email})</option>)}
                  </select>
                </div>
              </div>
              
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Job Role</label>
                <div className="relative">
                  <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <select required value={newJobId} onChange={e=>setNewJobId(e.target.value)} className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 outline-none appearance-none cursor-pointer">
                    <option value="">Select Job...</option>
                    {jobs.map(j => <option key={j.id||j.job_id} value={j.id||j.job_id}>{j.title}</option>)}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Round Type</label>
                  <select required value={newRoundType} onChange={e=>setNewRoundType(e.target.value)} className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 outline-none appearance-none cursor-pointer">
                    {ROUNDS.filter(r=>r!=='All').map(r => <option key={r} value={r}>{r}</option>)}
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Date & Time</label>
                  <input required type="datetime-local" value={newTime} onChange={e=>setNewTime(e.target.value)} className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
                </div>
              </div>

              <div className="pt-4 flex justify-end gap-3 border-t border-gray-100 dark:border-gray-800">
                <button type="button" onClick={() => setShowScheduleModal(false)} className="px-5 py-2.5 text-sm font-semibold text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-navy-800 rounded-xl transition-colors">Cancel</button>
                <button type="submit" className="px-6 py-2.5 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-lg shadow-indigo-500/25 transition-all">Schedule</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
