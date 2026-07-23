export interface User {
  id: string;
  name: string;
  email: string;
  phone?: string;
}

export interface Application {
  id: string;
  jobId: string;
  jobTitle: string;
  status: ApplicationStatus;
  appliedAt: string;
  updatedAt: string;
  resumeUrl?: string;
}

export type ApplicationStatus = 'applied' | 'screening' | 'interview_pending' | 'interviewing' | 'reviewing' | 'accepted' | 'rejected';

export interface InterviewMessage {
  id: string;
  sender: 'interviewer' | 'candidate';
  content: string;
  timestamp: string;
}
