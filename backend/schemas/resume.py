"""Resume schemas."""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ResumeUploadResponse(BaseModel):
    filename: str
    url: str
    size: int
    message: str = "Resume uploaded successfully"

class ResumeAnalysisResponse(BaseModel):
    candidate_id: str
    parsed_text: str
    skills: List[str]
    projects: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    companies: List[str]
    experience: List[Dict[str, Any]]
    certifications: List[str]
    ats_score: float
    resume_score: float
    missing_keywords: List[str]
