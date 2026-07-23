import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, UserPlus, Star, ArrowUpDown, Award } from 'lucide-react';
import { apiClient } from '../utils/api';

export default function Candidates() {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [stageFilter, setStageFilter] = useState<string>('all');
  const [sortByBest, setSortByBest] = useState<boolean>(true);

  useEffect(() => {
    async function fetchCandidates() {
      try {
        const res = await apiClient.get('/candidates');
        const list = res.data?.data || [];
        setCandidates(list);
      } catch (err) {
        console.warn('Could not fetch live candidates list:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchCandidates();
  }, []);

  const filteredCandidates = candidates
    .filter(c => {
      if (stageFilter !== 'all') {
        const stage = (c.pipeline_stage || c.stage || 'applied').toLowerCase();
        if (stage !== stageFilter.toLowerCase()) return false;
      }
      if (!search) return true;
      const term = search.toLowerCase();
      return (
        c.name?.toLowerCase().includes(term) ||
        c.email?.toLowerCase().includes(term) ||
        c.job_title?.toLowerCase().includes(term)
      );
    })
    .sort((a, b) => {
      if (sortByBest) {
        const scoreA = Number(a.atsScore ?? a.overallMatch ?? a.overallScore ?? 85);
        const scoreB = Number(b.atsScore ?? b.overallMatch ?? b.overallScore ?? 85);
        return scoreB - scoreA;
      }
      return (a.name || '').localeCompare(b.name || '');
    });

  return (
    <div className="animate-fade-in h-full flex flex-col">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold dark:text-white flex items-center gap-2">
            Candidates & ATS Records
          </h1>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Intelligent candidate screening powered by AST parsing & AI job-fit matching.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSortByBest(!sortByBest)}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 border transition-all ${
              sortByBest
                ? 'bg-amber-500/10 border-amber-500/30 text-amber-500 dark:text-amber-400'
                : 'bg-gray-100 dark:bg-navy-800 border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300'
            }`}
          >
            <Award className="w-4 h-4" />
            {sortByBest ? 'Sorted by Best Match (ATS Score ↓)' : 'Sort Alphabetically'}
          </button>
        </div>
      </div>
      
      <div className="glass-card p-4 mb-6 flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input 
            type="text" 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by candidate name, email, or job title..." 
            className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-navy-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm" 
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={stageFilter}
            onChange={(e) => setStageFilter(e.target.value)}
            className="py-2 px-3 bg-gray-50 dark:bg-navy-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm dark:text-white"
          >
            <option value="all">All Pipeline Stages</option>
            <option value="applied">Applied</option>
            <option value="screening">Screening</option>
            <option value="interview">Interview</option>
            <option value="technical">Technical</option>
            <option value="offer">Offer</option>
          </select>
        </div>
      </div>

      <div className="glass-card flex-1 overflow-hidden flex flex-col">
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-8 text-center text-sm text-gray-500">Loading candidate records...</div>
          ) : filteredCandidates.length === 0 ? (
            <div className="p-12 text-center">
              <UserPlus className="w-10 h-10 mx-auto text-gray-400 mb-3" />
              <h3 className="text-sm font-semibold dark:text-white">No candidates found</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Try clearing your search filters or upload a new resume.
              </p>
            </div>
          ) : (
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-gray-500 uppercase bg-gray-50/50 dark:bg-navy-900/50 border-b border-gray-200 dark:border-gray-800">
                <tr>
                  <th className="px-6 py-4 font-medium">Candidate Name</th>
                  <th className="px-6 py-4 font-medium">Target Role</th>
                  <th className="px-6 py-4 font-medium">Pipeline Stage</th>
                  <th className="px-6 py-4 font-medium">ATS Match Score</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredCandidates.map((c, idx) => {
                  const score = Math.round(Number(c.atsScore ?? c.overallMatch ?? c.overallScore ?? 85));
                  const isTopCandidate = score >= 80;
                  const badgeColor =
                    score >= 80
                      ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
                      : score >= 65
                      ? 'bg-amber-500/10 text-amber-500 border-amber-500/20'
                      : 'bg-red-500/10 text-red-500 border-red-500/20';

                  return (
                    <tr key={c.id || c.candidate_id || idx} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50/50 dark:hover:bg-navy-800/50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="relative">
                            <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold mr-3">
                              {(c.name || 'C').charAt(0).toUpperCase()}
                            </div>
                            {isTopCandidate && (
                              <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400 absolute -top-1 right-2" />
                            )}
                          </div>
                          <div>
                            <div className="font-semibold dark:text-white flex items-center gap-1.5">
                              {c.name || 'Candidate'}
                              {isTopCandidate && (
                                <span className="px-1.5 py-0.5 text-[10px] bg-amber-400/20 text-amber-500 font-bold rounded">
                                  BEST
                                </span>
                              )}
                            </div>
                            <div className="text-xs text-gray-500">{c.email || 'N/A'}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 dark:text-gray-300 font-medium">{c.job_title || 'Software Engineer'}</td>
                      <td className="px-6 py-4">
                        <span className="px-2.5 py-1 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 font-medium capitalize">
                          {c.pipeline_stage || c.stage || 'Applied'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2.5 py-1 text-xs font-bold rounded-lg border ${badgeColor}`}>
                          {score}% {isTopCandidate ? '• Top Match' : ''}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Link to={`/candidates/${c.id || c.candidate_id}`} className="text-primary hover:underline font-medium">
                          View Profile
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

