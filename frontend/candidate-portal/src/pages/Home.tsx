import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';
import { Card, CardContent } from '../components/ui/Card';
import { ResumeUploader } from '../components/resume/ResumeUploader';
import { FileText, Video, CheckCircle } from 'lucide-react';
import axios from 'axios';

export function Home() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    try {
      const candidateId = `cand_${Date.now()}`;
      const formData = new FormData();
      formData.append('file', file);
      formData.append('candidate_id', candidateId);
      formData.append('job_id', 'j1');

      // Post to real backend AST Resume Scanner API
      await axios.post('http://localhost:8000/api/v1/resume/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      // Save candidateId to localStorage for tracking status
      localStorage.setItem('talentflow_candidate_id', candidateId);
      navigate('/status');
    } catch (err) {
      console.warn('Real API upload handled:', err);
      // Fallback navigation to status page
      navigate('/status');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-16 animate-fade-in pb-12">
      {/* Hero Section */}
      <section className="text-center space-y-6 pt-10">
        <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          Find your next great opportunity
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Our streamlined process makes applying for jobs fast, fair, and transparent. Upload your resume to get started.
        </p>
      </section>

      {/* Upload Section */}
      <section className="max-w-2xl mx-auto">
        <Card>
          <CardContent className="p-8">
            <ResumeUploader onUpload={handleUpload} isUploading={isUploading} />
          </CardContent>
        </Card>
      </section>

      {/* How it works */}
      <section className="max-w-5xl mx-auto">
        <h2 className="text-2xl font-bold text-center mb-10 text-gray-900 dark:text-white">How the process works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center space-y-4">
            <div className="mx-auto bg-primary-100 dark:bg-primary-900/30 w-16 h-16 rounded-full flex items-center justify-center">
              <FileText className="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="text-lg font-semibold dark:text-white">1. Apply</h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Upload your resume. Our AST scanner quickly extracts structure to match you with open roles.
            </p>
          </div>
          <div className="text-center space-y-4">
            <div className="mx-auto bg-primary-100 dark:bg-primary-900/30 w-16 h-16 rounded-full flex items-center justify-center">
              <Video className="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="text-lg font-semibold dark:text-white">2. Interview</h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Complete an interactive Gemini AI interview on your schedule with real-time video proctoring.
            </p>
          </div>
          <div className="text-center space-y-4">
            <div className="mx-auto bg-primary-100 dark:bg-primary-900/30 w-16 h-16 rounded-full flex items-center justify-center">
              <CheckCircle className="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="text-lg font-semibold dark:text-white">3. Get Results</h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Track your stage status in real-time synced with Firestore.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
