from pydantic import BaseModel
from typing import Optional
from .models import ResumeAnalysis, ResumeScore

class ResumeUploadRequest(BaseModel):
    job_id: str

class ResumeAnalysisResponse(BaseModel):
    message: str
    analysis: ResumeAnalysis
    score: ResumeScore

class ResumeScoreResponse(BaseModel):
    score: ResumeScore
