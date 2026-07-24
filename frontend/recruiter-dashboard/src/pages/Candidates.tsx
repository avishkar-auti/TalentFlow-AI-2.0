import React, { useState, useEffect } from 'react';
import { Search, Filter, Download, UserPlus, FileText, CheckCircle2, Calendar, Copy, X, SlidersHorizontal } from 'lucide-react';
import { Link } from 'react-router-dom';
import { apiClient } from '../utils/api';

export default function Candidates() {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [search, setSearch] = useState('');
  const [jobFilter, setJobFilter] = useState('');
  const [atsThreshold, setAtsThreshold] = useState(0);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  // Modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [activeCandidate, setActiveCandidate] = useState<any>(null);

  // Add Candidate Form
  const [addName, setAddName] = useState('');
  const [addEmail, setAddEmail] = useState('');
  const [addJobId, setAddJobId] = useState('');

  // Schedule Interview Form
  const [scheduleType, setScheduleType] = useState('AI Screening');
  const [scheduleTime, setScheduleTime] = useState('');
  const [copiedId, setCopiedId] = useState('');

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [candRes, jobsRes] = await Promise.all([
          apiClient.get('/candidates').catch(() => null),
          apiClient.get('/jobs').catch(() => null)
        ]);

        let candList = candRes?.data?.data || candRes?.data || [];
        if (!candList.length) {
          candList = [
            { id: 'C-101', name: 'Alice Smith', email: 'alice@example.com', job_id: 'JOB-20260724-ABC123', atsScore: 92, pipeline_stage: 'shortlisted', skills_match: 95, exp_match: 90, edu_match: 85 },
            { id: 'C-102', name: 'Bob Johnson', email: 'bob@example.com', job_id: 'JOB-20260724-ABC123', atsScore: 65, pipeline_stage: 'applied', skills_match: 60, exp_match: 70, edu_match: 70 },
            { id: 'C-103', name: 'Charlie Davis', email: 'charlie@example.com', job_id: 'JOB-20260724-XYZ789', atsScore: 82, pipeline_stage: 'interview', skills_match: 80, exp_match: 85, edu_match: 80 },
          ];
        }
        // Normalize field names
        candList = candList.map(c => ({
          ...c,
          ats_score: c.atsScore || c.ats_score || 0,
          stage: c.pipeline_stage || c.stage || 'applied'
        }));
        setCandidates(candList);

        let jobsList = jobsRes?.data?.data || jobsRes?.data || [];
        setJobs(jobsList);
      } catch (err) {
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();

    // Auto-refresh every 5 seconds to catch new applications
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedIds(new Set(filteredCandidates.map(c => c.id)));
    } else {
      setSelectedIds(new Set());
    }
  };

  const handleSelect = (id: string) => {
    const newSet = new Set(selectedIds);
    if (newSet.has(id)) newSet.delete(id);
    else newSet.add(id);
    setSelectedIds(newSet);
  };

  const copyJobId = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(id);
    setCopiedId(id);
    setTimeout(() => setCopiedId(''), 2000);
  };

  const handleAddCandidate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/candidates', { name: addName, email: addEmail, job_id: addJobId, status: 'Applied' });
      setShowAddModal(false);
      // Refresh candidates ideally
      setAddName(''); setAddEmail(''); setAddJobId('');
    } catch (err) {
      console.error(err);
    }
  };

  const handleScheduleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/interviews', {
        candidate_id: activeCandidate?.id,
        job_id: activeCandidate?.job_id,
        round_type: scheduleType,
        scheduled_time: scheduleTime,
        status: 'Scheduled'
      });
      setShowScheduleModal(false);
      setActiveCandidate(null);
      setScheduleTime('');
    } catch (err) {
      console.error(err);
    }
  };

  const exportCSV = () => {
    const headers = ['Name,Email,JobID,ATS,Stage\n'];
    const rows = filteredCandidates.map(c => `${c.name},${c.email},${c.job_id},${c.ats_score},${c.stage}`).join('\n');
    const blob = new Blob([headers + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'candidates.csv';
    a.click();
  };

  const filteredCandidates = candidates.filter(c => {
    const matchesSearch = c.name?.toLowerCase().includes(search.toLowerCase()) || c.email?.toLowerCase().includes(search.toLowerCase());
    const matchesJob = jobFilter ? c.job_id === jobFilter : true;
    const matchesAts = (c.ats_score || 0) >= atsThreshold;
    return matchesSearch && matchesJob && matchesAts;
  });

  const getStageColor = (stage: string) => {
    const s = stage?.toLowerCase() || '';
    if (s.includes('shortlist') || s.includes('offer')) return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-500/30';
    if (s.includes('applied')) return 'bg-gray-100 text-gray-800 dark:bg-navy-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600';
    if (s.includes('screen')) return 'bg-blue-100 text-blue-800 dark:bg-blue-500/20 dark:text-blue-300 border border-blue-200 dark:border-blue-500/30';
    if (s.includes('interview') || s.includes('round')) return 'bg-amber-100 text-amber-800 dark:bg-amber-500/20 dark:text-amber-300 border border-amber-200 dark:border-amber-500/30';
    return 'bg-indigo-100 text-indigo-800 dark:bg-indigo-500/20 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30';
  };

  return (
    <div className="animate-fade-in pb-10 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-end gap-4 mb-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Talent Pool</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Manage applicants, ATS scores, and interview schedules.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={exportCSV} className="px-4 py-2 bg-white dark:bg-navy-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 rounded-xl text-sm font-medium hover:bg-gray-50 dark:hover:bg-navy-700 transition-colors flex items-center gap-2">
            <Download className="w-4 h-4" /> Export
          </button>
          <button onClick={() => setShowAddModal(true)} className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-500/25 flex items-center gap-2">
            <UserPlus className="w-4 h-4" /> Add Candidate
          </button>
        </div>
      </div>

      <div className="bg-white/60 dark:bg-navy-800/60 backdrop-blur-xl border border-gray-200 dark:border-gray-700 p-4 rounded-2xl flex flex-col md:flex-row gap-4 shadow-sm">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input 
            type="text" placeholder="Search name or email..." value={search} onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-900 text-sm focus:ring-2 focus:ring-indigo-500 outline-none text-gray-900 dark:text-white"
          />
        </div>
        <div className="w-full md:w-48 relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <select 
            value={jobFilter} onChange={(e) => setJobFilter(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-900 text-sm focus:ring-2 focus:ring-indigo-500 outline-none text-gray-900 dark:text-white appearance-none"
          >
            <option value="">All Jobs</option>
            {jobs.map(j => <option key={j.id || j.job_id} value={j.id || j.job_id}>{j.title}</option>)}
          </select>
        </div>
        <div className="flex items-center gap-3 w-full md:w-auto px-2">
          <SlidersHorizontal className="w-4 h-4 text-gray-400" />
          <div className="flex-1 min-w-[120px]">
            <input type="range" min="0" max="100" value={atsThreshold} onChange={(e) => setAtsThreshold(Number(e.target.value))} className="w-full accent-indigo-600" />
          </div>
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300 w-10">&gt;{atsThreshold}</span>
        </div>
      </div>

      <div className="bg-white/80 dark:bg-navy-900/80 backdrop-blur-xl border border-gray-200 dark:border-gray-700 rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50/50 dark:bg-navy-800/50 border-b border-gray-200 dark:border-gray-700">
                <th className="p-4 w-12"><input type="checkbox" checked={selectedIds.size === filteredCandidates.length && filteredCandidates.length > 0} onChange={handleSelectAll} className="rounded text-indigo-600 focus:ring-indigo-500 bg-white dark:bg-navy-950 border-gray-300 dark:border-gray-600" /></th>
                <th className="p-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Candidate</th>
                <th className="p-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Job ID</th>
                <th className="p-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">ATS Score</th>
                <th className="p-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Stage</th>
                <th className="p-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {loading ? (
                <tr><td colSpan={6} className="p-8 text-center text-gray-500">Loading...</td></tr>
              ) : filteredCandidates.length === 0 ? (
                <tr><td colSpan={6} className="p-8 text-center text-gray-500">No candidates found.</td></tr>
              ) : (
                filteredCandidates.map(cand => (
                  <tr key={cand.id} className="hover:bg-gray-50 dark:hover:bg-navy-800/50 transition-colors group">
                    <td className="p-4"><input type="checkbox" checked={selectedIds.has(cand.id)} onChange={() => handleSelect(cand.id)} className="rounded text-indigo-600 focus:ring-indigo-500 bg-white dark:bg-navy-950 border-gray-300 dark:border-gray-600" /></td>
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold shadow-sm">
                          {cand.name.charAt(0)}
                        </div>
                        <div>
                          <p className="text-sm font-bold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{cand.name}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">{cand.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="inline-flex items-center gap-2 group/id cursor-pointer bg-gray-50 dark:bg-navy-950 px-2.5 py-1 rounded-lg border border-gray-200 dark:border-gray-700" onClick={(e) => copyJobId(cand.job_id, e)}>
                        <span className="text-xs font-mono text-gray-600 dark:text-gray-400">{cand.job_id}</span>
                        {copiedId === cand.job_id ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5 text-gray-400 group-hover/id:text-indigo-500" />}
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <span className={`text-lg font-bold ${cand.ats_score >= 70 ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'}`}>{cand.ats_score}%</span>
                        <div className="w-16 h-1.5 flex bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                          <div className="bg-indigo-500 h-full" style={{ width: `${cand.skills_match || cand.ats_score}%` }}></div>
                          <div className="bg-emerald-500 h-full" style={{ width: `${cand.exp_match || 0}%` }}></div>
                          <div className="bg-amber-500 h-full" style={{ width: `${cand.edu_match || 0}%` }}></div>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${getStageColor(cand.stage)}`}>
                        {cand.stage || 'Applied'}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex justify-end gap-2">
                        {cand.ats_score >= 70 && cand.stage === 'Applied' && (
                          <button className="p-2 bg-emerald-50 text-emerald-600 hover:bg-emerald-100 dark:bg-emerald-500/10 dark:text-emerald-400 dark:hover:bg-emerald-500/20 rounded-lg transition-colors border border-emerald-100 dark:border-emerald-500/20" title="Shortlist">
                            <CheckCircle2 className="w-4 h-4" />
                          </button>
                        )}
                        {(cand.stage === 'Shortlisted' || cand.stage?.includes('Interview')) && (
                          <button onClick={() => { setActiveCandidate(cand); setShowScheduleModal(true); }} className="p-2 bg-indigo-50 text-indigo-600 hover:bg-indigo-100 dark:bg-indigo-500/10 dark:text-indigo-400 dark:hover:bg-indigo-500/20 rounded-lg transition-colors border border-indigo-100 dark:border-indigo-500/20" title="Schedule Interview">
                            <Calendar className="w-4 h-4" />
                          </button>
                        )}
                        <Link to={`/candidates/${cand.id}`} className="p-2 bg-gray-50 text-gray-600 hover:bg-gray-200 dark:bg-navy-800 dark:text-gray-300 dark:hover:bg-navy-700 rounded-lg transition-colors border border-gray-200 dark:border-gray-600">
                          <FileText className="w-4 h-4" />
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modals */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-navy-900 rounded-2xl w-full max-w-md shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center bg-gray-50/50 dark:bg-navy-800/50">
              <h3 className="font-bold text-gray-900 dark:text-white">Add Candidate</h3>
              <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleAddCandidate} className="p-6 space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-1">Name</label>
                <input required type="text" value={addName} onChange={e=>setAddName(e.target.value)} className="w-full px-3 py-2 border rounded-xl dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white" />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-1">Email</label>
                <input required type="email" value={addEmail} onChange={e=>setAddEmail(e.target.value)} className="w-full px-3 py-2 border rounded-xl dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white" />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-1">Job Role</label>
                <select required value={addJobId} onChange={e=>setAddJobId(e.target.value)} className="w-full px-3 py-2 border rounded-xl dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white">
                  <option value="">Select Job...</option>
                  {jobs.map(j => <option key={j.id||j.job_id} value={j.id||j.job_id}>{j.title}</option>)}
                </select>
              </div>
              <div className="pt-4 flex justify-end gap-2">
                <button type="button" onClick={() => setShowAddModal(false)} className="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-navy-800 rounded-xl">Cancel</button>
                <button type="submit" className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl">Add</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showScheduleModal && activeCandidate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-3xl w-full max-w-md shadow-2xl border border-slate-700 overflow-hidden">
            <div className="px-8 py-6 border-b border-slate-700 flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-white">Schedule Interview</h2>
                <p className="text-slate-400 text-sm mt-1">Set up a new meeting</p>
              </div>
              <button onClick={() => setShowScheduleModal(false)} className="text-slate-400 hover:text-white transition"><X className="w-6 h-6" /></button>
            </div>

            <form onSubmit={handleScheduleSubmit} className="p-8 space-y-6">
              {/* Candidate Info */}
              <div className="space-y-3">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Candidate</label>
                <div className="px-4 py-3 bg-slate-700/50 rounded-xl border border-slate-600 text-white font-medium">{activeCandidate.name}</div>
              </div>

              {/* Job Role */}
              <div className="space-y-3">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Job Role</label>
                <div className="px-4 py-3 bg-slate-700/50 rounded-xl border border-slate-600 text-white font-medium">{activeCandidate.job_id}</div>
              </div>

              {/* Round Type */}
              <div className="space-y-3">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Round Type</label>
                <select value={scheduleType} onChange={e=>setScheduleType(e.target.value)} className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition">
                  <option value="AI Screening" className="bg-slate-800">AI Screening</option>
                  <option value="HR Round" className="bg-slate-800">HR Round</option>
                  <option value="Technical Coding" className="bg-slate-800">Technical Coding</option>
                </select>
              </div>

              {/* Date & Time */}
              <div className="space-y-3">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Date & Time</label>
                <input required type="datetime-local" value={scheduleTime} onChange={e=>setScheduleTime(e.target.value)} className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition" />
              </div>

              {/* Buttons */}
              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={() => setShowScheduleModal(false)} className="px-6 py-2.5 text-sm font-semibold text-slate-300 hover:text-white transition">Cancel</button>
                <button type="submit" className="px-6 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-700 hover:to-indigo-600 rounded-xl transition shadow-lg">Schedule</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
