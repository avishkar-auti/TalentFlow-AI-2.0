"""Interview schemas."""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..shared.enums import InterviewStatus, ProctoringFlag
from ..models.interview import Interview

class ScheduleInterviewRequest(BaseModel):
    candidate_id: str
    job_id: str
    scheduled_at: datetime
    duration_minutes: int = 60
    interviewer_type: str = "ai"

class InterviewResponse(BaseModel):
    id: str
    candidate_id: str
    job_id: str
    scheduled_at: datetime
    duration_minutes: int
    status: InterviewStatus
    proctoring_flags: List[ProctoringFlag]
    interviewer_type: str
    created_at: datetime

class InterviewSessionMessage(BaseModel):
    sender: str # ai, candidate
    message: str
    timestamp: datetime

class ProctoringFlagSchema(BaseModel):
    flag_type: ProctoringFlag
    timestamp: datetime
    details: Optional[str] = None
