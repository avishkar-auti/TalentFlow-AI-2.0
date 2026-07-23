import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, UserPlus } from 'lucide-react';
import { apiClient } from '../utils/api';

export default function Candidates() {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

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

  const filteredCandidates = candidates.filter(c => {
    if (!search) return true;
    const term = search.toLowerCase();
    return (
      c.name?.toLowerCase().includes(term) ||
      c.email?.toLowerCase().includes(term) ||
      c.job_title?.toLowerCase().includes(term)
    );
  });

  return (
    <div className="animate-fade-in h-full flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold dark:text-white">All Candidates</h1>
          <p className="text-xs text-gray-500 dark:text-gray-400">Manage candidates and parsed ATS resume records.</p>
        </div>
      </div>
      
      <div className="glass-card p-4 mb-6 flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input 
            type="text" 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name, email, or skills..." 
            className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-navy-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm" 
          />
        </div>
      </div>

      <div className="glass-card flex-1 overflow-hidden flex flex-col">
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-8 text-center text-sm text-gray-500">Loading candidates...</div>
          ) : filteredCandidates.length === 0 ? (
            <div className="p-12 text-center">
              <UserPlus className="w-10 h-10 mx-auto text-gray-400 mb-3" />
              <h3 className="text-sm font-semibold dark:text-white">No candidates found</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Upload a candidate resume or create an application to populate the database.
              </p>
            </div>
          ) : (
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-gray-500 uppercase bg-gray-50/50 dark:bg-navy-900/50 border-b border-gray-200 dark:border-gray-800">
                <tr>
                  <th className="px-6 py-4 font-medium">Candidate Name</th>
                  <th className="px-6 py-4 font-medium">Applied Job</th>
                  <th className="px-6 py-4 font-medium">Stage</th>
                  <th className="px-6 py-4 font-medium">ATS Match Score</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredCandidates.map((c) => (
                  <tr key={c.id || c.candidate_id} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50/50 dark:hover:bg-navy-800/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold mr-3">
                          {(c.name || 'C').charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div className="font-medium dark:text-white">{c.name || 'Candidate'}</div>
                          <div className="text-xs text-gray-500">{c.email || 'N/A'}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 dark:text-gray-300">{c.job_title || 'Target Position'}</td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 font-medium capitalize">
                        {c.pipeline_stage || 'Applied'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-green-500 font-semibold">{c.atsScore || c.overallMatch || 85}%</span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link to={`/candidates/${c.id || c.candidate_id}`} className="text-primary hover:underline font-medium">
                        View Profile
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
