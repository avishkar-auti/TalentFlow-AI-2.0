from pydantic import BaseModel
from typing import Optional
from .models import BackgroundCheckResult

class BackgroundCheckRequest(BaseModel):
    pass # No body needed if candidate_id and job_id are in path/query

class BackgroundCheckResponse(BaseModel):
    candidate_id: str
    job_id: str
    result: BackgroundCheckResult
