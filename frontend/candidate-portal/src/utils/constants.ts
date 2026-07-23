export const API_BASE_URL = 'http://localhost:8000/api/v1';
export const WS_BASE_URL = 'ws://localhost:8000/ws';

export const APPLICATION_STAGES = [
  { id: 'applied', label: 'Application Received' },
  { id: 'screening', label: 'Resume Review' },
  { id: 'interview_pending', label: 'Interview Scheduled' },
  { id: 'reviewing', label: 'Final Decision' }
];

export const STATUS_MESSAGES: Record<string, string> = {
  applied: "We've received your application and will review it shortly.",
  screening: "Your resume is currently being reviewed by our team.",
  interview_pending: "Great news! We'd like to invite you to an interview.",
  interviewing: "Your interview is currently in progress or being evaluated.",
  reviewing: "We are preparing a final decision on your application.",
  accepted: "Congratulations! We would like to extend an offer.",
  rejected: "Thank you for applying. Unfortunately, we will not be moving forward at this time."
};
