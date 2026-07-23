export const PIPELINE_STAGES = [
  { id: 'applied', title: 'Applied' },
  { id: 'screening', title: 'Screening' },
  { id: 'review', title: 'Recruiter Review' },
  { id: 'interview_scheduled', title: 'Interview Scheduled' },
  { id: 'interview_completed', title: 'Interview Completed' },
  { id: 'decision', title: 'Decision' },
  { id: 'hired', title: 'Hired' },
  { id: 'rejected', title: 'Rejected' }
];

export const STAGE_COLORS: Record<string, string> = {
  applied: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  screening: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
  review: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300',
  interview_scheduled: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
  interview_completed: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
  decision: 'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300',
  hired: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  rejected: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
};
