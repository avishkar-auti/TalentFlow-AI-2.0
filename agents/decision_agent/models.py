from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class ScoreBreakdown(BaseModel):
    resume_score: float
    ats_score: float
    matching_score: float
    background_score: float
    technical_score: float
    speech_score: float

class DecisionResult(BaseModel):
    candidate_id: str
    job_id: str
    overall_score: float
    recommendation: str
    strengths: list[str]
    concerns: list[str]
    remarks: str
    score_breakdown: ScoreBreakdown
    created_at: datetime = Field(default_factory=datetime.utcnow)
