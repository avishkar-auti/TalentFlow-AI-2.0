from pydantic import BaseModel
from typing import List, Optional
from .models import MatchingResult

class MatchRequest(BaseModel):
    job_id: str

class MatchResponse(BaseModel):
    success: bool
    data: Optional[MatchingResult] = None
    error: Optional[str] = None
