import React from 'react';
import { useParams, Link } from 'react-router-dom';

export default function JobDetail() {
  const { id } = useParams();
  
  return (
    <div className="animate-fade-in">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link to="/jobs" className="text-sm text-primary hover:underline mb-2 inline-block">← Back to Jobs</Link>
          <h1 className="text-2xl font-bold dark:text-white">Frontend Engineer</h1>
          <p className="text-gray-500">Pipeline for Job ID: {id}</p>
        </div>
      </div>
      <div className="glass-card p-6 flex items-center justify-center h-96">
        <p className="text-gray-500">Job specific pipeline board goes here (similar to main Pipeline)</p>
      </div>
    </div>
  );
}
