"""Report model."""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from ..shared.enums import Recommendation
from ..shared.helpers import utc_now, generate_id

class Report(BaseModel):
    id: str = Field(default_factory=generate_id)
    candidate_id: str
    job_id: str
    scores: Dict[str, float] = Field(default_factory=dict)
    recommendation: Recommendation
    remarks: str = ""
    generated_at: datetime = Field(default_factory=utc_now)
    pdf_url: Optional[str] = None
