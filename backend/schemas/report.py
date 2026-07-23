"""Report schemas."""
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from ..shared.enums import Recommendation

class ScoreSummary(BaseModel):
    category: str
    score: float
    details: Optional[str] = None

class ReportResponse(BaseModel):
    id: str
    candidate_id: str
    job_id: str
    scores: Dict[str, float]
    score_summaries: Optional[list[ScoreSummary]] = None
    recommendation: Recommendation
    remarks: str
    generated_at: datetime
    pdf_url: Optional[str] = None
