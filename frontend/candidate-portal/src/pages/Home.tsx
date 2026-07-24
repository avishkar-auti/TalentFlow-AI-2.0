import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';
import { Card, CardContent } from '../components/ui/Card';
import { ResumeUploader } from '../components/resume/ResumeUploader';
import { FileText, Video, CheckCircle, Briefcase, MapPin, Award, CheckCircle2, ChevronRight } from 'lucide-react';
import axios from 'axios';

export function Home() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [isUploading, setIsUploading] = useState(false);
  const [jobs, setJobs] = useState<any[]>([]);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const [selectedJobId, setSelectedJobId] = useState<string>('');

  useEffect(() => {
    async function fetchJobs() {
      try {
        const res = await axios.get('http://localhost:8000/api/v1/jobs');
        const list = res.data?.data || [];
        setJobs(list);
        if (list.length > 0) {
          const firstId = list[0].id || list[0].job_id || 'j1';
          setSelectedJobId(firstId);
        }
      } catch (err) {
        console.warn('Error fetching live job postings for candidates:', err);
      } finally {
        setLoadingJobs(false);
      }
    }
    fetchJobs();
  }, []);

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    try {
      const candidateId = `cand_${Date.now()}`;
      const chosenJobId = selectedJobId || (jobs.length > 0 ? (jobs[0].id || jobs[0].job_id) : 'JOB001');

      const formData = new FormData();
      formData.append('file', file);
      formData.append('candidate_id', candidateId);
      formData.append('job_id', chosenJobId);

      // Post to real backend AST Resume Scanner API
      const uploadRes = await axios.post('http://localhost:8000/api/v1/resume/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const analysisData = uploadRes?.data?.data || uploadRes?.data;
      if (analysisData) {
        localStorage.setItem('talentflow_latest_resume_analysis', JSON.stringify(analysisData));
      }

      // Save candidateId and target jobId to localStorage for tracking status
      localStorage.setItem('talentflow_candidate_id', candidateId);
      localStorage.setItem('talentflow_applied_job_id', chosenJobId);
      navigate('/status');
    } catch (err) {
      console.warn('Real API upload handled:', err);
      // Fallback navigation to status page
      navigate('/status');
    } finally {
      setIsUploading(false);
    }
  };

  const selectedJob = jobs.find(j => (j.id || j.job_id) === selectedJobId) || jobs[0];

  return (
    <div className="space-y-12 animate-fade-in pb-16">
      {/* Hero Section */}
      <section className="text-center space-y-4 pt-8">
        <span className="px-3.5 py-1 text-xs font-bold uppercase tracking-wider bg-primary-100 text-primary-700 dark:bg-primary-900/40 dark:text-primary-300 rounded-full inline-block mb-2">
          ⚡ AI-Powered Talent Matcher
        </span>
        <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          Apply to Live Open Positions
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Explore job requisitions created by HR in real-time. Select a position and upload your resume to generate your instant AST match score.
        </p>
      </section>

      {/* HR Job Openings Display */}
      <section className="max-w-5xl mx-auto space-y-4">
        <div className="flex justify-between items-center px-2">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-primary-500" /> Active Job Openings
          </h2>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {jobs.length} roles posted by HR
          </span>
        </div>

        {loadingJobs ? (
          <div className="p-8 text-center text-sm text-gray-500 bg-gray-50 dark:bg-gray-800/40 rounded-2xl">
            Loading live job requisitions...
          </div>
        ) : jobs.length === 0 ? (
          <div className="p-8 text-center text-sm text-gray-500 bg-gray-50 dark:bg-gray-800/40 rounded-2xl">
            No open positions posted at the moment. Please check back shortly!
          </div>
        ) : (
          <div className="grid md:grid-cols-3 gap-4">
            {jobs.map((job) => {
              const jobId = job.id || job.job_id || job.jobId;
              const isSelected = selectedJobId === jobId;
              const skillsList = job.requiredSkills || (job.requirements && job.requirements.skills) || ['Python', 'FastAPI', 'React'];

              return (
                <div
                  key={jobId}
                  onClick={() => setSelectedJobId(jobId)}
                  className={`p-5 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between ${
                    isSelected
                      ? 'bg-primary-50/50 dark:bg-primary-900/20 border-primary-500 shadow-md ring-2 ring-primary-500/20'
                      : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-primary-300'
                  }`}
                >
                  <div>
                    <div className="flex justify-between items-start mb-2">
                      <span className="px-2.5 py-0.5 text-[10px] font-bold uppercase rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                        {job.status || 'Active'}
                      </span>
                      {isSelected && (
                        <CheckCircle2 className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                      )}
                    </div>
                    <h3 className="font-bold text-gray-900 dark:text-white text-base mb-1">
                      {job.title}
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-2 mb-3">
                      <span>{job.department || 'Engineering'}</span> • 
                      <span className="flex items-center gap-0.5"><MapPin className="w-3 h-3" />{job.location || 'Remote'}</span>
                    </p>

                    <div className="flex flex-wrap gap-1 mb-4">
                      {skillsList.slice(0, 4).map((skill: string, idx: number) => (
                        <span key={idx} className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-[11px] font-medium rounded-md">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <button
                    type="button"
                    className={`w-full py-2 text-xs font-semibold rounded-xl transition flex items-center justify-center gap-1 ${
                      isSelected
                        ? 'bg-primary-600 text-white shadow-sm'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-primary-500 hover:text-white'
                    }`}
                  >
                    {isSelected ? 'Role Selected for Application' : 'Select Position'}
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Upload Section */}
      <section className="max-w-2xl mx-auto space-y-3">
        {selectedJob && (
          <div className="bg-primary-50 dark:bg-primary-950/40 border border-primary-200 dark:border-primary-800 p-4 rounded-2xl flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-primary-700 dark:text-primary-300 uppercase tracking-wider">
                Applying For
              </p>
              <h4 className="text-base font-bold text-gray-900 dark:text-white">
                {selectedJob.title} ({selectedJob.department || 'Engineering'})
              </h4>
            </div>
            <span className="text-xs px-2.5 py-1 bg-primary-600 text-white font-medium rounded-lg">
              Role Linked
            </span>
          </div>
        )}

        <Card>
          <CardContent className="p-8">
            <ResumeUploader onUpload={handleUpload} isUploading={isUploading} />
          </CardContent>
        </Card>
      </section>

      {/* How it works */}
      <section className="max-w-5xl mx-auto pt-4">
        <h2 className="text-2xl font-bold text-center mb-10 text-gray-900 dark:text-white">How the process works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center space-y-4">
            <div className="mx-auto bg-primary-100 dark:bg-primary-900/30 w-16 h-16 rounded-full flex items-center justify-center">
              <FileText className="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="text-lg font-semibold dark:text-white">1. Select Job & Apply</h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Pick a role posted by HR. Upload your resume to run AST structure extraction and match scoring.
            </p>
          </div>
          <div className="text-center space-y-4">
            <div className="mx-auto bg-primary-100 dark:bg-primary-900/30 w-16 h-16 rounded-full flex items-center justify-center">
              <Video className="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="text-lg font-semibold dark:text-white">2. AI Video Interview</h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Complete an interactive AI interview with live proctoring & questions tailored to your resume chunks.
            </p>
          </div>
          <div className="text-center space-y-4">
            <div className="mx-auto bg-primary-100 dark:bg-primary-900/30 w-16 h-16 rounded-full flex items-center justify-center">
              <CheckCircle className="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="text-lg font-semibold dark:text-white">3. Real-Time Tracking</h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Track candidate status in real-time synced across Candidate & Recruiter dashboards.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

