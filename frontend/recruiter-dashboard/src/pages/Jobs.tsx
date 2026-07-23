import React, { useState, useEffect } from 'react';
import { Plus, Users, MapPin, Briefcase, X } from 'lucide-react';
import { Link } from 'react-router-dom';
import { apiClient } from '../utils/api';

export default function Jobs() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState('');
  const [department, setDepartment] = useState('Engineering');
  const [location, setLocation] = useState('Remote');
  const [skillsStr, setSkillsStr] = useState('Python, FastAPI, React, Docker');

  async function fetchJobs() {
    try {
      const res = await apiClient.get('/jobs');
      const list = res.data?.data || [];
      setJobs(list);
    } catch (err) {
      console.warn('Could not fetch jobs from API:', err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title) return;

    const skillsList = skillsStr.split(',').map(s => s.trim()).filter(Boolean);
    const newJobPayload = {
      title,
      department,
      location,
      requirements: {
        skills: skillsList,
        experience: '2+ Years',
        education: 'Bachelor'
      },
      status: 'active'
    };

    try {
      await apiClient.post('/jobs', newJobPayload);
      setShowModal(false);
      setTitle('');
      fetchJobs();
    } catch (err) {
      console.warn('Job creation API warning:', err);
    }
  };

  return (
    <div className="animate-fade-in pb-10">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold dark:text-white">Active Jobs</h1>
          <p className="text-xs text-gray-500 dark:text-gray-400">Open reqs & requirements connected to Firestore.</p>
        </div>
        <button 
          onClick={() => setShowModal(true)}
          className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 transition shadow-lg shadow-primary/25 flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" /> Create Job
        </button>
      </div>

      {loading ? (
        <div className="p-8 text-center text-sm text-gray-500">Loading active jobs...</div>
      ) : jobs.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <Briefcase className="w-10 h-10 mx-auto text-gray-400 mb-3" />
          <h3 className="text-sm font-semibold dark:text-white">No active job postings</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 mb-4">
            Click 'Create Job' to post your first position.
          </p>
          <button 
            onClick={() => setShowModal(true)}
            className="inline-flex items-center px-4 py-2 bg-primary text-white rounded-lg text-xs font-semibold"
          >
            <Plus className="w-4 h-4 mr-1" /> Create First Job
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <div key={job.id || job.job_id} className="glass-card p-6 group hover:border-primary/50 transition-colors">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <span className="text-xs font-medium px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 rounded-full capitalize">
                    {job.status || 'Active'}
                  </span>
                  <h3 className="text-lg font-bold dark:text-white mt-3">{job.title}</h3>
                  <p className="text-sm text-gray-500 mt-1">{job.department || 'Engineering'}</p>
                </div>
              </div>
              
              <div className="space-y-2 mb-6">
                <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <MapPin className="w-4 h-4 mr-2" /> {job.location || 'Remote'}
                </div>
                <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <Briefcase className="w-4 h-4 mr-2" /> Full-time
                </div>
                <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <Users className="w-4 h-4 mr-2" /> {job.application_count || 0} Candidates
                </div>
              </div>
              
              <Link 
                to={`/jobs/${job.id || job.job_id}`} 
                className="block w-full text-center py-2 bg-gray-100 dark:bg-navy-800 hover:bg-gray-200 dark:hover:bg-navy-700 text-sm font-medium rounded-lg transition-colors text-gray-700 dark:text-gray-300"
              >
                View Pipeline
              </Link>
            </div>
          ))}
        </div>
      )}

      {/* Modal to Create Job */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-fade-in">
          <div className="bg-white dark:bg-navy-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-xl border border-gray-200 dark:border-gray-700">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Create New Job Req</h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateJob} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Job Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Senior Python Developer"
                  className="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-navy-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Department</label>
                <input
                  type="text"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-navy-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Required Skills (comma separated)</label>
                <input
                  type="text"
                  value={skillsStr}
                  onChange={(e) => setSkillsStr(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-navy-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <div className="pt-4 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-navy-700 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-primary hover:bg-primary/90 rounded-lg shadow-sm"
                >
                  Post Job
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
