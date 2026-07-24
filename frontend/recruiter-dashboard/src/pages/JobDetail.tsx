import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Users, MapPin, Briefcase, ChevronLeft, Calendar, FileText, CheckCircle2, TrendingUp, Filter, SlidersHorizontal, UserPlus } from 'lucide-react';
import { apiClient } from '../utils/api';

const PIPELINE_STAGES = ['Applied', 'Screened', 'Shortlisted', 'AI Interview', 'HR Round', 'Technical', 'Offer'];

export default function JobDetail() {
  const { id } = useParams();
  const [job, setJob] = useState<any>(null);
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [atsThreshold, setAtsThreshold] = useState(0);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        // Fetch Job Details
        const jobRes = await apiClient.get(`/jobs/${id}`).catch(() => null);
        const jobData = jobRes?.data?.data || jobRes?.data || {
          id: id,
          title: 'Senior Frontend Engineer',
          department: 'Engineering',
          location: 'Remote',
          status: 'Active',
          description: 'We are looking for a Senior Frontend Engineer to join our core team. You will be responsible for architecture and implementation of our next-gen products.',
          requirements: { skills: ['React', 'TypeScript', 'Next.js', 'Tailwind CSS'] }
        };
        setJob(jobData);

        // Fetch Pipeline / Candidates
        // If API fails, mock candidates for the kanban
        const candRes = await apiClient.get(`/jobs/${id}/candidates`).catch(() => null);
        let candList = candRes?.data?.data || candRes?.data || [];
        
        if (!candList.length) {
          candList = [
            { id: 'C-1', name: 'Alice Smith', email: 'alice@example.com', ats_score: 92, stage: 'Shortlisted' },
            { id: 'C-2', name: 'Bob Johnson', email: 'bob@example.com', ats_score: 65, stage: 'Screened' },
            { id: 'C-3', name: 'Charlie Davis', email: 'charlie@example.com', ats_score: 78, stage: 'Applied' },
            { id: 'C-4', name: 'Diana Prince', email: 'diana@example.com', ats_score: 88, stage: 'Technical' },
            { id: 'C-5', name: 'Evan Wright', email: 'evan@example.com', ats_score: 95, stage: 'Offer' },
            { id: 'C-6', name: 'Fiona Gallagher', email: 'fiona@example.com', ats_score: 45, stage: 'Applied' },
          ];
        }
        setCandidates(candList);
      } catch (err) {
        console.error('Error fetching job details', err);
      } finally {
        setLoading(false);
      }
    }
    if (id) fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-gray-500 dark:text-gray-400">Loading pipeline...</p>
      </div>
    );
  }

  if (!job) {
    return <div className="p-8 text-center text-red-500">Job not found.</div>;
  }

  // Filter candidates by ATS Threshold
  const filteredCandidates = candidates.filter(c => (c.ats_score || 0) >= atsThreshold);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-500/10 border-emerald-200 dark:border-emerald-500/20';
    if (score >= 60) return 'text-amber-600 dark:text-amber-400 bg-amber-100 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/20';
    return 'text-rose-600 dark:text-rose-400 bg-rose-100 dark:bg-rose-500/10 border-rose-200 dark:border-rose-500/20';
  };

  const avgAts = candidates.length ? Math.round(candidates.reduce((acc, c) => acc + (c.ats_score || 0), 0) / candidates.length) : 0;
  const shortlistedCount = candidates.filter(c => ['Shortlisted', 'AI Interview', 'HR Round', 'Technical', 'Offer'].includes(c.stage)).length;

  return (
    <div className="animate-fade-in pb-10 flex flex-col h-[calc(100vh-80px)] overflow-hidden">
      {/* Header */}
      <div className="shrink-0 mb-6 space-y-6">
        <Link to="/jobs" className="inline-flex items-center text-sm text-gray-500 hover:text-indigo-600 dark:text-gray-400 dark:hover:text-indigo-400 transition-colors">
          <ChevronLeft className="w-4 h-4 mr-1" /> Back to Jobs
        </Link>
        
        <div className="bg-white/60 dark:bg-navy-800/60 backdrop-blur-xl border border-gray-200 dark:border-gray-700 rounded-2xl p-6 shadow-sm">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
            <div className="space-y-4 flex-1">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">{job.title}</h1>
                  <span className="px-2.5 py-1 text-xs font-semibold rounded-md bg-indigo-100 text-indigo-700 dark:bg-indigo-500/20 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30">
                    {job.id || job.job_id || 'JOB-UNKNOWN'}
                  </span>
                  <span className={`px-2.5 py-1 text-xs font-semibold rounded-md border ${job.status?.toLowerCase() === 'active' ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20' : 'bg-gray-100 text-gray-700 border-gray-200 dark:bg-navy-900 dark:text-gray-300'}`}>
                    {job.status || 'Active'}
                  </span>
                </div>
                <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-center"><Briefcase className="w-4 h-4 mr-1.5" /> {job.department}</div>
                  <div className="flex items-center"><MapPin className="w-4 h-4 mr-1.5" /> {job.location}</div>
                </div>
              </div>

              <p className="text-sm text-gray-600 dark:text-gray-400 max-w-3xl leading-relaxed">
                {job.description}
              </p>

              {job.requirements?.skills && (
                <div className="flex flex-wrap gap-2">
                  {job.requirements.skills.map((skill: string, i: number) => (
                    <span key={i} className="px-2.5 py-1 bg-gray-100 dark:bg-navy-900 text-gray-700 dark:text-gray-300 text-xs font-medium rounded-lg border border-gray-200 dark:border-gray-700">
                      {skill}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div className="flex flex-row md:flex-col gap-4">
              <div className="bg-white dark:bg-navy-900 p-4 rounded-xl border border-gray-100 dark:border-gray-700 text-center min-w-[120px]">
                <p className="text-xs text-gray-500 mb-1">Total Applicants</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white flex items-center justify-center gap-2"><Users className="w-5 h-5 text-indigo-500" /> {candidates.length}</p>
              </div>
              <div className="bg-white dark:bg-navy-900 p-4 rounded-xl border border-gray-100 dark:border-gray-700 text-center min-w-[120px]">
                <p className="text-xs text-gray-500 mb-1">Avg ATS Score</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white flex items-center justify-center gap-2"><TrendingUp className="w-5 h-5 text-emerald-500" /> {avgAts}%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center justify-between bg-white/60 dark:bg-navy-800/60 backdrop-blur-xl border border-gray-200 dark:border-gray-700 p-3 rounded-xl shadow-sm">
          <div className="flex items-center gap-4 px-2">
            <SlidersHorizontal className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Min ATS Score: {atsThreshold}%</span>
            <input 
              type="range" 
              min="0" max="100" 
              value={atsThreshold} 
              onChange={(e) => setAtsThreshold(Number(e.target.value))}
              className="w-48 accent-indigo-600"
            />
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400 px-2">
            Showing {filteredCandidates.length} of {candidates.length} candidates
          </div>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="flex-1 overflow-x-auto pb-4 custom-scrollbar">
        <div className="flex gap-6 h-full min-w-max px-1">
          {PIPELINE_STAGES.map(stage => {
            const stageCandidates = filteredCandidates.filter(c => (c.stage || 'Applied') === stage);
            
            return (
              <div key={stage} className="w-80 flex flex-col h-full bg-gray-50/50 dark:bg-navy-900/30 border border-gray-200 dark:border-gray-700/50 rounded-2xl overflow-hidden">
                <div className="p-4 border-b border-gray-200 dark:border-gray-700/50 bg-gray-100/50 dark:bg-navy-800/50 flex justify-between items-center shrink-0">
                  <h3 className="font-semibold text-gray-900 dark:text-white text-sm">{stage}</h3>
                  <span className="bg-white dark:bg-navy-950 text-gray-600 dark:text-gray-400 text-xs px-2 py-0.5 rounded-full font-medium border border-gray-200 dark:border-gray-700">
                    {stageCandidates.length}
                  </span>
                </div>
                
                <div className="flex-1 overflow-y-auto p-3 space-y-3 custom-scrollbar">
                  {stageCandidates.map(cand => (
                    <div key={cand.id} className="bg-white dark:bg-navy-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md hover:border-indigo-300 dark:hover:border-indigo-500/50 transition-all group">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h4 className="font-bold text-gray-900 dark:text-white text-sm">{cand.name}</h4>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{cand.email}</p>
                        </div>
                        <div className={`px-2 py-1 text-xs font-bold rounded-md border ${getScoreColor(cand.ats_score || 0)}`}>
                          {cand.ats_score || 0}%
                        </div>
                      </div>
                      
                      <div className="flex justify-between items-center mt-4">
                        <Link to={`/candidates/${cand.id}`} className="text-xs text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
                          View Profile
                        </Link>
                        
                        {stage === 'Shortlisted' && (
                          <button className="flex items-center gap-1 text-xs px-2.5 py-1.5 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 dark:bg-indigo-500/10 dark:text-indigo-300 dark:hover:bg-indigo-500/20 rounded-md font-medium transition-colors">
                            <Calendar className="w-3.5 h-3.5" /> Schedule
                          </button>
                        )}
                        {stage === 'Applied' && (
                          <button className="flex items-center gap-1 text-xs px-2.5 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-500/10 dark:text-emerald-300 dark:hover:bg-emerald-500/20 rounded-md font-medium transition-colors">
                            <CheckCircle2 className="w-3.5 h-3.5" /> Shortlist
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                  {stageCandidates.length === 0 && (
                    <div className="h-24 flex items-center justify-center border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-xl">
                      <p className="text-xs text-gray-400">No candidates</p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
