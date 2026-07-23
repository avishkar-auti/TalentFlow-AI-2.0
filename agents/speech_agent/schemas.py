"""API schemas for Speech Agent."""
from pydantic import BaseModel, Field

class SpeechAnalysisRequest(BaseModel):
    """Request schema for speech analysis."""
    candidate_id: str = Field(..., description="The ID of the candidate")
    interview_id: str = Field(..., description="The ID of the interview")

class SpeechAnalysisResponse(BaseModel):
    """Response schema for speech analysis."""
    success: bool
    message: str
    data: dict = Field(default_factory=dict)
