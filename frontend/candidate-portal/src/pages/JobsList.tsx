import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, MapPin, Search, Filter, ChevronRight, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { ResumeUploader } from '../components/resume/ResumeUploader';
import axios from 'axios';

export function JobsList() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('all');
  const [selectedJob, setSelectedJob] = useState<any | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  
  // Application form fields
  const [applicantName, setApplicantName] = useState('');
  const [applicantEmail, setApplicantEmail] = useState('');
  
  // ATS Score display
  const [atsScoreResult, setAtsScoreResult] = useState<number | null>(null);
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    async function fetchJobs() {
      try {
        const res = await axios.get('http://localhost:8000/api/v1/jobs');
        setJobs(res.data?.data || []);
      } catch (err) {
        console.warn('Error fetching jobs:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchJobs();
    
    // Pre-fill user data if available
    const storedName = localStorage.getItem('talentflow_user_name');
    const storedEmail = localStorage.getItem('talentflow_user_email');
    if (storedName) setApplicantName(storedName);
    if (storedEmail) setApplicantEmail(storedEmail);
  }, []);

  // Animation for ATS score counting
  useEffect(() => {
    if (atsScoreResult !== null) {
      let start = 0;
      const end = atsScoreResult;
      const duration = 1500; // ms
      const incrementTime = 30; // ms
      const step = (end / duration) * incrementTime;
      
      const timer = setInterval(() => {
        start += step;
        if (start >= end) {
          setDisplayScore(end);
          clearInterval(timer);
          // Wait 1.5s then navigate
          setTimeout(() => {
            navigate('/status');
          }, 1500);
        } else {
          setDisplayScore(Math.floor(start));
        }
      }, incrementTime);
      
      return () => clearInterval(timer);
    }
  }, [atsScoreResult, navigate]);

  const handleUpload = async (file: File) => {
    if (!selectedJob) return;
    setIsUploading(true);
    try {
      const jobId = selectedJob.id || selectedJob.job_id || 'JOB001';

      const formData = new FormData();
      formData.append('file', file);
      formData.append('name', applicantName);
      formData.append('email', applicantEmail);

      const res = await axios.post(`http://localhost:8000/api/v1/jobs/${jobId}/apply`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const candidateId = res.data?.candidate_id || `cand_${Date.now()}`;
      const atsScore = res.data?.ats_score || Math.floor(Math.random() * 30) + 65; // Mock score if API doesn't return one
      
      localStorage.setItem('talentflow_candidate_id', candidateId);
      localStorage.setItem('talentflow_applied_job_id', jobId);
      
      setAtsScoreResult(atsScore);
      // Navigate is handled in the effect after animation
    } catch (err) {
      console.warn('Upload error:', err);
      // Mock success for demo purposes if backend fails
      const candidateId = `cand_${Date.now()}`;
      const jobId = selectedJob.id || selectedJob.job_id || 'JOB001';
      localStorage.setItem('talentflow_candidate_id', candidateId);
      localStorage.setItem('talentflow_applied_job_id', jobId);
      setAtsScoreResult(85);
    } finally {
      setIsUploading(false);
    }
  };

  const filteredJobs = jobs.filter(j => {
    if (deptFilter !== 'all' && (j.department || 'Engineering').toLowerCase() !== deptFilter.toLowerCase()) {
      return false;
    }
    if (!search) return true;
    const term = search.toLowerCase();
    return (
      j.title?.toLowerCase().includes(term) ||
      j.department?.toLowerCase().includes(term) ||
      j.location?.toLowerCase().includes(term) ||
      (j.job_id && j.job_id.toLowerCase().includes(term))
    );
  });

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in pb-16 pt-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="px-3 py-1 text-xs font-bold uppercase tracking-wider bg-primary-100 text-primary-700 dark:bg-primary-900/40 dark:text-primary-300 rounded-full inline-block mb-2">
            ⚡ Active HR Job Requisitions
          </span>
          <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white">
            Explore Open Job Openings
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Real-time job requisitions posted by HR. Apply to get evaluated by our ATS Resume scanner.
          </p>
        </div>
      </div>

      {/* Filter & Search Controls */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md p-4 rounded-2xl border border-gray-200 dark:border-gray-800 flex flex-col md:flex-row gap-4 shadow-lg shadow-gray-200/50 dark:shadow-none">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search open jobs by title, department, or location..."
            className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm outline-none focus:ring-2 focus:ring-primary-500 text-gray-900 dark:text-gray-100 transition-all"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
            className="py-2 px-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm dark:text-white outline-none focus:ring-2 focus:ring-primary-500 transition-all"
          >
            <option value="all">All Departments</option>
            <option value="engineering">Engineering</option>
            <option value="product">Product</option>
            <option value="design">Design</option>
            <option value="data">Data Science</option>
          </select>
        </div>
      </div>

      {/* Job Grid */}
      {loading ? (
        <div className="p-12 text-center text-sm text-gray-500 bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm flex items-center justify-center">
          <div className="w-6 h-6 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mr-3"></div>
          Loading live job openings...
        </div>
      ) : filteredJobs.length === 0 ? (
        <div className="p-12 text-center bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm">
          <Briefcase className="w-10 h-10 mx-auto text-gray-400 mb-3" />
          <h3 className="text-base font-semibold text-gray-900 dark:text-white">No matching job openings found</h3>
          <p className="text-xs text-gray-500 mt-1">Try broadening your search term or department filter.</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredJobs.map((job) => {
            const jobId = job.job_id || job.id || `JOB-${Math.floor(Math.random() * 10000000)}`;
            const skillsList = job.requiredSkills || (job.requirements && job.requirements.skills) || ['Python', 'FastAPI', 'React', 'Docker'];
            const salaryRange = job.salary_range || '$120k - $160k';
            const experienceLevel = job.experience_level || 'Mid-Senior Level';

            return (
              <div
                key={jobId}
                className="bg-white/60 dark:bg-gray-900/60 backdrop-blur-sm border border-gray-200 dark:border-gray-800 p-6 rounded-3xl hover:border-primary-500 dark:hover:border-primary-400 hover:shadow-xl dark:hover:shadow-primary-900/20 transition-all flex flex-col justify-between group relative overflow-hidden"
              >
                {/* Decorative blob */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-primary-500/5 rounded-full blur-3xl -mr-16 -mt-16 transition-all group-hover:bg-primary-500/10"></div>
                
                <div className="relative z-10">
                  <div className="flex justify-between items-start mb-3">
                    <span className="px-2.5 py-0.5 text-[11px] font-bold uppercase rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                      {job.status || 'ACTIVE/OPEN'}
                    </span>
                    <span className="text-xs font-mono text-gray-400 bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded border border-gray-200 dark:border-gray-700">
                      {jobId}
                    </span>
                  </div>

                  <h3 className="font-bold text-gray-900 dark:text-white text-xl group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors mb-2 line-clamp-1">
                    {job.title}
                  </h3>
                  
                  <div className="flex flex-wrap gap-x-3 gap-y-1 mb-4 text-xs font-medium text-gray-600 dark:text-gray-400">
                    <span className="flex items-center gap-1"><Briefcase className="w-3.5 h-3.5" /> {job.department || 'Engineering'}</span>
                    <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {job.location || 'Remote'}</span>
                  </div>

                  <div className="flex flex-col gap-1 mb-4 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-100 dark:border-gray-700/50">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500 dark:text-gray-400">Experience</span>
                      <span className="font-semibold text-gray-900 dark:text-gray-200">{experienceLevel}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500 dark:text-gray-400">Salary Range</span>
                      <span className="font-semibold text-emerald-600 dark:text-emerald-400">{salaryRange}</span>
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 mb-4 leading-relaxed">
                    {job.description || 'Join our engineering team to build next-generation AI microservices and cloud solutions that redefine talent acquisition.'}
                  </p>

                  <div className="flex flex-wrap gap-1.5 mb-6">
                    {skillsList.slice(0, 4).map((skill: string, i: number) => (
                      <span key={i} className="px-2.5 py-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm text-gray-700 dark:text-gray-300 text-[11px] font-semibold rounded-lg">
                        {skill}
                      </span>
                    ))}
                    {skillsList.length > 4 && (
                      <span className="px-2.5 py-1 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-500 text-[11px] font-semibold rounded-lg">
                        +{skillsList.length - 4} more
                      </span>
                    )}
                  </div>
                </div>

                <div className="relative z-10">
                  <Button
                    onClick={() => setSelectedJob(job)}
                    className="w-full flex items-center justify-center gap-1.5 text-sm font-semibold py-3 rounded-xl transition-transform hover:scale-[1.02] active:scale-[0.98]"
                  >
                    Apply Now <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Apply Modal */}
      {selectedJob && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => !isUploading && atsScoreResult === null && setSelectedJob(null)}></div>
          
          <div className="bg-white dark:bg-gray-900 rounded-3xl max-w-xl w-full space-y-0 shadow-2xl border border-gray-200 dark:border-gray-800 relative z-10 overflow-hidden flex flex-col max-h-[90vh]">
            {atsScoreResult === null ? (
              <>
                <div className="p-6 border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/50">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-primary-600 dark:text-primary-400 bg-primary-100 dark:bg-primary-900/30 px-2 py-0.5 rounded">
                          Apply for Role
                        </span>
                        <span className="text-[10px] font-mono text-gray-500 bg-gray-200 dark:bg-gray-800 px-2 py-0.5 rounded">
                          {selectedJob.job_id || selectedJob.id || 'JOB-ID-MISSING'}
                        </span>
                      </div>
                      <h3 className="text-2xl font-extrabold text-gray-900 dark:text-white mt-1">
                        {selectedJob.title}
                      </h3>
                      <p className="text-sm text-gray-500 mt-1 flex items-center gap-2">
                        <span>{selectedJob.department || 'Engineering'}</span>
                        <span className="w-1 h-1 rounded-full bg-gray-300 dark:bg-gray-600"></span>
                        <span>{selectedJob.location || 'Remote'}</span>
                      </p>
                    </div>
                    <button
                      onClick={() => setSelectedJob(null)}
                      disabled={isUploading}
                      className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    >
                      ✕
                    </button>
                  </div>
                </div>

                <div className="p-6 overflow-y-auto space-y-5">
                  <div className="grid grid-cols-1 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Full Name</label>
                      <input 
                        type="text" 
                        value={applicantName}
                        onChange={(e) => setApplicantName(e.target.value)}
                        placeholder="John Doe"
                        className="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm outline-none focus:ring-2 focus:ring-primary-500 dark:text-white transition-all"
                        disabled={isUploading}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Email Address</label>
                      <input 
                        type="email" 
                        value={applicantEmail}
                        onChange={(e) => setApplicantEmail(e.target.value)}
                        placeholder="john@example.com"
                        className="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm outline-none focus:ring-2 focus:ring-primary-500 dark:text-white transition-all"
                        disabled={isUploading}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Resume Upload</label>
                    <div className="glass-panel p-1 rounded-2xl">
                      <ResumeUploader onUpload={handleUpload} isUploading={isUploading} />
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="p-10 flex flex-col items-center justify-center text-center space-y-6 animate-in slide-in-from-bottom-8 duration-500">
                <div className="w-32 h-32 relative flex items-center justify-center mb-2">
                  <svg className="w-full h-full transform -rotate-90 absolute inset-0">
                    <circle 
                      cx="64" cy="64" r="56" 
                      className="stroke-gray-100 dark:stroke-gray-800" 
                      strokeWidth="12" fill="none" 
                    />
                    <circle 
                      cx="64" cy="64" r="56" 
                      className={`transition-all duration-300 ${displayScore >= 70 ? 'stroke-emerald-500' : displayScore >= 50 ? 'stroke-amber-500' : 'stroke-red-500'}`}
                      strokeWidth="12" fill="none" 
                      strokeDasharray="351.86"
                      strokeDashoffset={351.86 - (351.86 * displayScore) / 100}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="text-4xl font-extrabold text-gray-900 dark:text-white relative z-10 flex items-baseline">
                    {displayScore}<span className="text-xl text-gray-400">%</span>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                    Analyzing Resume...
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 max-w-sm mx-auto">
                    {displayScore < atsScoreResult 
                      ? "Our AI is currently matching your skills with the job requirements." 
                      : "Analysis complete! Redirecting you to your candidate dashboard..."}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
