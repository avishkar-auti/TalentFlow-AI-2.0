from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class MatchingResult(BaseModel):
    candidate_id: str
    job_id: str
    skill_match: float
    experience_match: float
    education_match: float
    location_match: float
    overall_match: float
    missing_skills: List[str]
    transferable_skills: List[str] = []
    confidence: float
    reasoning: str = ""
    llm_adjusted: bool = False
