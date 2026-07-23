export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

export interface Candidate {
  id: string;
  name: string;
  email: string;
  jobId: string;
  jobTitle: string;
  stage: string;
  matchScore: number;
  appliedDate: string;
  timeInStage: number; // days
  resumeUrl?: string;
  skills: string[];
  experience: { title: string; company: string; duration: string }[];
  education: { degree: string; institution: string; year: string }[];
}

export interface Job {
  id: string;
  title: string;
  department: string;
  location: string;
  type: string;
  status: 'Open' | 'Closed' | 'Draft';
  candidatesCount: number;
  createdAt: string;
}

export interface DashboardStats {
  totalCandidates: number;
  openJobs: number;
  interviewsToday: number;
  hiringRate: number; // percentage
}

export interface Activity {
  id: string;
  type: string;
  description: string;
  timestamp: string;
}

export interface PipelineStage {
  id: string;
  title: string;
}
