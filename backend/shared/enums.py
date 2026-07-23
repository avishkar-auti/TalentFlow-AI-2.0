"""Enums for TalentFlow-AI."""
from enum import Enum

class PipelineStage(str, Enum):
    APPLIED = "applied"
    SCREENING = "screening"
    RECRUITER_REVIEW = "recruiter_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    DECISION = "decision"
    HIRED = "hired"
    REJECTED = "rejected"

class CandidateStatus(str, Enum):
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"
    REJECTED = "rejected"
    HIRED = "hired"
    HOLD = "hold"

class Recommendation(str, Enum):
    STRONG_HIRE = "strong_hire"
    HIRE = "hire"
    MAYBE = "maybe"
    NO_HIRE = "no_hire"
    STRONG_NO_HIRE = "strong_no_hire"

class LLMProvider(str, Enum):
    GROQ = "groq"
    GEMINI = "gemini"

class AgentName(str, Enum):
    RESUME_PARSER = "resume_parser"
    RESUME_SCORER = "resume_scorer"
    SKILL_EXTRACTOR = "skill_extractor"
    INTERVIEW_PROCTOR = "interview_proctor"
    INTERVIEW_EVALUATOR = "interview_evaluator"
    REPORT_GENERATOR = "report_generator"

class UserRole(str, Enum):
    ADMIN = "admin"
    RECRUITER = "recruiter"
    CANDIDATE = "candidate"

class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"
    NO_SHOW = "no_show"

class ProctoringFlag(str, Enum):
    MULTIPLE_FACES = "multiple_faces"
    NO_FACE = "no_face"
    LOOKING_AWAY = "looking_away"
    BACKGROUND_NOISE = "background_noise"
    TAB_SWITCH = "tab_switch"

class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
