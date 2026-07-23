from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class InterviewPhase(str, Enum):
    CONSENT = "consent"
    INTRO = "intro"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CLOSING = "closing"
    ENDED = "ended"

class SessionStatus(str, Enum):
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ABORTED = "aborted"

class InterviewTurn(BaseModel):
    speaker: str = Field(description="'interviewer' or 'candidate'")
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    phase: InterviewPhase

class ProctoringFlagType(str, Enum):
    MULTIPLE_FACES = "multiple_faces"
    NO_FACE = "no_face"
    LOOKING_AWAY = "looking_away"
    TAB_SWITCH = "tab_switch"

class ProctoringFlag(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    flag_type: ProctoringFlagType
    description: str
    severity: str = Field(description="'low', 'medium', 'high'")
    
class ProctoringResult(BaseModel):
    flags: List[ProctoringFlag] = []
    
class InterviewSession(BaseModel):
    interview_id: str
    candidate_id: str
    job_id: str
    status: SessionStatus = SessionStatus.INITIALIZED
    current_phase: InterviewPhase = InterviewPhase.CONSENT
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    turns: List[InterviewTurn] = []
    proctoring: ProctoringResult = Field(default_factory=ProctoringResult)

class InterviewerResponse(BaseModel):
    message: str
    next_phase: Optional[InterviewPhase] = None

class InterviewResult(BaseModel):
    interview_id: str
    status: SessionStatus
    transcript: List[InterviewTurn]
    proctoring_summary: Dict[str, Any]
    completion_time: datetime
