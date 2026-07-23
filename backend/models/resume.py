"""Resume analysis model."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ResumeAnalysis(BaseModel):
    parsed_text: str = ""
    skills: List[str] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    companies: List[str] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    ats_score: float = 0.0
    resume_score: float = 0.0
    missing_keywords: List[str] = Field(default_factory=list)
