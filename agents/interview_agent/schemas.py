from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import InterviewPhase, SessionStatus

class InterviewStartRequest(BaseModel):
    candidate_id: str
    job_id: str

class InterviewStartResponse(BaseModel):
    interview_id: str
    ws_url: str
    status: SessionStatus

class InterviewStatusResponse(BaseModel):
    interview_id: str
    status: SessionStatus
    current_phase: InterviewPhase
    start_time: Optional[datetime]
    
class TranscriptResponse(BaseModel):
    interview_id: str
    turns: List[Dict[str, Any]]

class ProctoringResponse(BaseModel):
    interview_id: str
    flags: List[Dict[str, Any]]
