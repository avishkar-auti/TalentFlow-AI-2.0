from pydantic import BaseModel
from typing import List
from .models import DecisionResult

class DecisionRequest(BaseModel):
    candidate_id: str
    job_id: str

class DecisionResponse(BaseModel):
    success: bool
    data: DecisionResult
