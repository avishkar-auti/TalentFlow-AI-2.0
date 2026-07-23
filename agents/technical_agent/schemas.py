"""API schemas for Technical Agent."""
from pydantic import BaseModel, Field

class TechnicalEvaluationRequest(BaseModel):
    """Request schema for technical evaluation."""
    candidate_id: str = Field(..., description="The ID of the candidate")
    interview_id: str = Field(..., description="The ID of the interview")

class TechnicalEvaluationResponse(BaseModel):
    """Response schema for technical evaluation."""
    success: bool
    message: str
    data: dict = Field(default_factory=dict)
