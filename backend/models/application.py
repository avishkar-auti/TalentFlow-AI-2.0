from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class Application(BaseModel):
    id: Optional[str] = None
    candidate_id: str
    job_id: str
    status: str = "applied"
    applied_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
