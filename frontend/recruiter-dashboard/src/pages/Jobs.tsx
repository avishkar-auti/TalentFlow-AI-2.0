import React, { useState, useEffect } from 'react';
import { Plus, Users, MapPin, Briefcase, X, Copy, Edit2, Trash2, CheckCircle2, Clock, XCircle, Search, Filter } from 'lucide-react';
import { Link } from 'react-router-dom';
import { apiClient } from '../utils/api';

export default function Jobs() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [copiedId, setCopiedId] = useState('');

  // Modal State
  const [title, setTitle] = useState('');
  const [department, setDepartment] = useState('Engineering');
  const [location, setLocation] = useState('Remote');
  const [description, setDescription] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('Mid');
  const [salaryRange, setSalaryRange] = useState('');
  const [type, setType] = useState('Full-time');
  const [skills, setSkills] = useState<string[]>([]);
  const [skillInput, setSkillInput] = useState('');

  async function fetchJobs() {
    try {
      const res = await apiClient.get('/jobs');
      const list = res.data?.data || res.data || [];
      setJobs(Array.isArray(list) ? list : []);
    } catch (err) {
      console.warn('Could not fetch jobs:', err);
      // Fallback data for showcase
      setJobs([
        {
          id: 'JOB-20260724-ABC123',
          title: 'Senior React Developer',
          department: 'Engineering',
          location: 'Remote',
          type: 'Full-time',
          status: 'Active',
          application_count: 45,
          requirements: { skills: ['React', 'TypeScript', 'Tailwind'] }
        },
        {
          id: 'JOB-20260724-XYZ789',
          title: 'Product Designer',
          department: 'Design',
          location: 'New York, NY',
          type: 'Contract',
          status: 'Paused',
          application_count: 12,
          requirements: { skills: ['Figma', 'UI/UX', 'Prototyping'] }
        }
      ]);
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

    const newJobPayload = {
      title,
      department,
      location,
      description,
      type,
      requirements: {
        skills,
        experience: experienceLevel,
        salary: salaryRange
      },
      status: 'Active'
    };

    try {
      await apiClient.post('/jobs', newJobPayload);
      setShowModal(false);
      resetModal();
      fetchJobs();
    } catch (err) {
      console.warn('Job creation warning:', err);
    }
  };

  const resetModal = () => {
    setTitle('');
    setDepartment('Engineering');
    setLocation('Remote');
    setDescription('');
    setExperienceLevel('Mid');
    setSalaryRange('');
    setType('Full-time');
    setSkills([]);
    setSkillInput('');
  };

  const handleAddSkill = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && skillInput.trim()) {
      e.preventDefault();
      if (!skills.includes(skillInput.trim())) {
        setSkills([...skills, skillInput.trim()]);
      }
      setSkillInput('');
    }
  };

  const removeSkill = (skillToRemove: string) => {
    setSkills(skills.filter(s => s !== skillToRemove));
  };

  const copyId = (id: string) => {
    navigator.clipboard.writeText(id);
    setCopiedId(id);
    setTimeout(() => setCopiedId(''), 2000);
  };

  const filteredJobs = jobs.filter(job => {
    const matchesSearch = job.department?.toLowerCase().includes(search.toLowerCase()) || 
                          job.title?.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter ? job.status?.toLowerCase() === statusFilter.toLowerCase() : true;
    return matchesSearch && matchesStatus;
  });

  const totalJobs = jobs.length;
  const activeJobs = jobs.filter(j => j.status?.toLowerCase() === 'active').length;
  const totalApplicants = jobs.reduce((acc, job) => acc + (job.application_count || 0), 0);

  const getStatusColor = (status: string) => {
    const s = status?.toLowerCase();
    if (s === 'active') return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
    if (s === 'paused') return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
    if (s === 'closed') return 'bg-rose-500/10 text-rose-500 border-rose-500/20';
    return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
  };

  const getStatusIcon = (status: string) => {
    const s = status?.toLowerCase();
    if (s === 'active') return <CheckCircle2 className="w-3 h-3 mr-1" />;
    if (s === 'paused') return <Clock className="w-3 h-3 mr-1" />;
    if (s === 'closed') return <XCircle className="w-3 h-3 mr-1" />;
    return null;
  };

  return (
    <div className="animate-fade-in pb-10 max-w-7xl mx-auto space-y-8">
      {/* Header & Stats */}
      <div>
        <div className="flex flex-col md:flex-row md:justify-between md:items-end gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 bg-clip-text text-transparent">Job Openings</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Manage job requisitions and track candidate pipelines</p>
          </div>
          <button 
            onClick={() => { resetModal(); setShowModal(true); }}
            className="bg-indigo-600 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-500/25 flex items-center justify-center gap-2 group"
          >
            <Plus className="w-4 h-4 group-hover:scale-110 transition-transform" /> 
            Create Job
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { label: 'Total Jobs', value: totalJobs, icon: Briefcase, color: 'text-blue-500' },
            { label: 'Active Openings', value: activeJobs, icon: CheckCircle2, color: 'text-emerald-500' },
            { label: 'Total Applicants', value: totalApplicants, icon: Users, color: 'text-purple-500' },
          ].map((stat, i) => (
            <div key={i} className="bg-white/50 dark:bg-navy-800/50 backdrop-blur-xl border border-gray-200 dark:border-gray-700 p-6 rounded-2xl flex items-center gap-4 shadow-sm">
              <div className={`p-3 rounded-xl bg-gray-100 dark:bg-navy-900 ${stat.color}`}>
                <stat.icon className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 bg-white/30 dark:bg-navy-800/30 p-4 rounded-2xl backdrop-blur-md border border-gray-200 dark:border-gray-700">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input 
            type="text" 
            placeholder="Search jobs or departments..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-900 text-sm focus:ring-2 focus:ring-indigo-500 outline-none text-gray-900 dark:text-white transition-all"
          />
        </div>
        <div className="relative min-w-[200px]">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full pl-10 pr-8 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-900 text-sm focus:ring-2 focus:ring-indigo-500 outline-none text-gray-900 dark:text-white appearance-none cursor-pointer transition-all"
          >
            <option value="">All Statuses</option>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="closed">Closed</option>
          </select>
        </div>
      </div>

      {/* Job Grid */}
      {loading ? (
        <div className="py-20 text-center flex flex-col items-center">
          <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-sm text-gray-500 dark:text-gray-400">Loading jobs...</p>
        </div>
      ) : filteredJobs.length === 0 ? (
        <div className="py-20 text-center bg-white/30 dark:bg-navy-800/30 rounded-3xl border border-gray-200 dark:border-gray-700 border-dashed">
          <Briefcase className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No jobs found</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-6 max-w-sm mx-auto">
            {search || statusFilter ? 'Try adjusting your filters or search terms.' : 'Get started by creating your first job requisition.'}
          </p>
          {!(search || statusFilter) && (
            <button onClick={() => setShowModal(true)} className="inline-flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-medium transition-all">
              <Plus className="w-4 h-4" /> Create First Job
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredJobs.map((job) => (
            <div key={job.id || job.job_id} className="group bg-white/70 dark:bg-navy-800/70 backdrop-blur-xl border border-gray-200 dark:border-gray-700 rounded-2xl p-6 hover:shadow-xl hover:shadow-indigo-500/10 hover:border-indigo-500/30 transition-all duration-300 flex flex-col h-full relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity translate-x-4 group-hover:translate-x-0">
                <button className="p-2 bg-white dark:bg-navy-900 text-gray-600 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 transition-colors">
                  <Edit2 className="w-4 h-4" />
                </button>
                <button className="p-2 bg-white dark:bg-navy-900 text-gray-600 dark:text-gray-300 hover:text-rose-600 dark:hover:text-rose-400 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 transition-colors">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div className="mb-4 pr-20">
                <div className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border mb-4 ${getStatusColor(job.status)}`}>
                  {getStatusIcon(job.status)}
                  {job.status || 'Active'}
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors line-clamp-1">{job.title}</h3>
                
                <div className="flex items-center gap-2 mt-2 group/id cursor-pointer" onClick={() => copyId(job.id || job.job_id)}>
                  <code className="text-xs font-mono bg-gray-100 dark:bg-navy-900 text-gray-600 dark:text-gray-400 px-2 py-1 rounded-md">
                    {job.id || job.job_id || 'JOB-UNKNOWN'}
                  </code>
                  <span className="text-gray-400 opacity-0 group-hover/id:opacity-100 transition-opacity">
                    {copiedId === (job.id || job.job_id) ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5 hover:text-indigo-500" />}
                  </span>
                </div>
              </div>
              
              <div className="space-y-3 mb-6 flex-grow">
                <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                  <Briefcase className="w-4 h-4 mr-2.5 text-gray-400" /> 
                  <span className="font-medium">{job.department}</span> 
                  <span className="mx-2 text-gray-300 dark:text-gray-600">•</span> 
                  {job.type || 'Full-time'}
                </div>
                <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                  <MapPin className="w-4 h-4 mr-2.5 text-gray-400" /> {job.location || 'Remote'}
                </div>
                <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                  <Users className="w-4 h-4 mr-2.5 text-gray-400" /> 
                  <span className="font-medium text-gray-900 dark:text-white">{job.application_count || 0}</span>&nbsp;Candidates
                </div>
              </div>

              {job.requirements?.skills && (
                <div className="flex flex-wrap gap-1.5 mb-6">
                  {job.requirements.skills.slice(0, 4).map((skill: string, i: number) => (
                    <span key={i} className="px-2 py-1 bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 text-xs rounded-md border border-indigo-100 dark:border-indigo-500/20">
                      {skill}
                    </span>
                  ))}
                  {job.requirements.skills.length > 4 && (
                    <span className="px-2 py-1 bg-gray-50 dark:bg-navy-900 text-gray-600 dark:text-gray-400 text-xs rounded-md border border-gray-200 dark:border-gray-700">
                      +{job.requirements.skills.length - 4}
                    </span>
                  )}
                </div>
              )}
              
              <Link 
                to={`/jobs/${job.id || job.job_id}`} 
                className="mt-auto block w-full text-center py-2.5 bg-gray-50 dark:bg-navy-900 hover:bg-indigo-50 dark:hover:bg-indigo-500/10 text-sm font-semibold rounded-xl transition-colors text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 border border-gray-200 dark:border-gray-700 hover:border-indigo-200 dark:hover:border-indigo-500/30"
              >
                View Pipeline
              </Link>
            </div>
          ))}
        </div>
      )}

      {/* Enhanced Create Job Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 animate-fade-in">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setShowModal(false)} />
          <div className="relative w-full max-w-3xl max-h-[90vh] flex flex-col bg-white dark:bg-navy-900 rounded-3xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
            
            <div className="px-6 py-5 border-b border-gray-100 dark:border-gray-800 flex justify-between items-center bg-gray-50/50 dark:bg-navy-800/50">
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">Create Job Requisition</h3>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Fill in the details to publish a new position.</p>
              </div>
              <button onClick={() => setShowModal(false)} className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-navy-800 rounded-full transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
              <form id="createJobForm" onSubmit={handleCreateJob} className="space-y-6">
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-1.5 md:col-span-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Job Title <span className="text-rose-500">*</span></label>
                    <input type="text" required value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Senior Frontend Engineer"
                      className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none transition-shadow" />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Department</label>
                    <input type="text" value={department} onChange={(e) => setDepartment(e.target.value)} placeholder="e.g. Engineering"
                      className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none transition-shadow" />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Location</label>
                    <input type="text" value={location} onChange={(e) => setLocation(e.target.value)} placeholder="e.g. San Francisco, CA or Remote"
                      className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none transition-shadow" />
                  </div>

                  <div className="space-y-1.5 md:col-span-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Job Description</label>
                    <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Brief description of the role..." rows={4}
                      className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none transition-shadow resize-none" />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Experience Level</label>
                    <select value={experienceLevel} onChange={(e) => setExperienceLevel(e.target.value)}
                      className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none appearance-none cursor-pointer">
                      <option value="Junior">Junior</option>
                      <option value="Mid">Mid</option>
                      <option value="Senior">Senior</option>
                      <option value="Lead">Lead</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Employment Type</label>
                    <select value={type} onChange={(e) => setType(e.target.value)}
                      className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none appearance-none cursor-pointer">
                      <option value="Full-time">Full-time</option>
                      <option value="Part-time">Part-time</option>
                      <option value="Contract">Contract</option>
                    </select>
                  </div>

                  <div className="space-y-1.5 md:col-span-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Salary Range</label>
                    <input type="text" value={salaryRange} onChange={(e) => setSalaryRange(e.target.value)} placeholder="e.g. $120,000 - $150,000"
                      className="w-full px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-950 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none transition-shadow" />
                  </div>

                  <div className="space-y-1.5 md:col-span-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Required Skills</label>
                    <div className="w-full p-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-navy-950 focus-within:ring-2 focus-within:ring-indigo-500 transition-shadow min-h-[52px] flex flex-wrap gap-2 items-center">
                      {skills.map((skill, idx) => (
                        <span key={idx} className="flex items-center gap-1.5 px-3 py-1 bg-indigo-50 dark:bg-indigo-500/20 text-indigo-700 dark:text-indigo-300 text-sm rounded-lg border border-indigo-100 dark:border-indigo-500/30">
                          {skill}
                          <button type="button" onClick={() => removeSkill(skill)} className="hover:text-indigo-900 dark:hover:text-indigo-100">
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </span>
                      ))}
                      <input type="text" value={skillInput} onChange={(e) => setSkillInput(e.target.value)} onKeyDown={handleAddSkill} placeholder={skills.length === 0 ? "Type a skill and press Enter" : "Add another skill..."}
                        className="flex-1 min-w-[120px] bg-transparent outline-none text-sm text-gray-900 dark:text-white px-2 py-1 placeholder-gray-400" />
                    </div>
                  </div>
                </div>

              </form>
            </div>

            <div className="px-6 py-4 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-navy-800/50 flex justify-end gap-3">
              <button type="button" onClick={() => setShowModal(false)} className="px-5 py-2.5 text-sm font-semibold text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-navy-700 rounded-xl transition-colors">
                Cancel
              </button>
              <button type="submit" form="createJobForm" className="px-6 py-2.5 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-lg shadow-indigo-500/25 transition-all">
                Publish Job
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
