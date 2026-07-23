"""Constants for TalentFlow-AI."""

PIPELINE_STAGES = [
    "applied",
    "screening",
    "recruiter_review",
    "interview_scheduled",
    "interview_completed",
    "decision",
    "hired",
    "rejected"
]

STAGE_DISPLAY_NAMES = {
    "applied": "Applied",
    "screening": "AI Screening",
    "recruiter_review": "Recruiter Review",
    "interview_scheduled": "Interview Scheduled",
    "interview_completed": "Interview Completed",
    "decision": "Decision Pending",
    "hired": "Hired",
    "rejected": "Rejected"
}

# Internal agent names, not shown to users
AGENT_NAMES = [
    "resume_parser",
    "resume_scorer",
    "skill_extractor",
    "interview_proctor",
    "interview_evaluator",
    "report_generator"
]

MAX_RESUME_SIZE_MB = 10
SUPPORTED_RESUME_FORMATS = [".pdf", ".docx", ".doc"]

USER_FACING_STATUS_MAP = {
    "resume_agent_completed": "Resume Analysis Complete",
    "resume_agent_failed": "Resume Analysis Failed",
    "interview_scheduled": "Interview Scheduled",
    "interview_proctor_flag": "Interview Proctoring Flag Raised",
    "report_generated": "Final Report Available"
}
