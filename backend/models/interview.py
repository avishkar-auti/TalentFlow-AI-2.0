"""Interview model."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any

class Interview(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: Optional[str] = None
    candidate_id: Optional[str] = Field(default=None, alias="candidateId")
    job_id: Optional[str] = Field(default=None, alias="jobId")
    scheduled_at: Optional[Any] = Field(default=None, alias="scheduledAt")
    duration_minutes: int = Field(default=45, alias="durationMinutes")
    status: str = "scheduled"
    proctoringFlags: List[Any] = Field(default_factory=list)
    interviewerType: str = "ai_gemini"
    created_at: Optional[Any] = Field(default=None, alias="createdAt")
    updated_at: Optional[Any] = Field(default=None, alias="updatedAt")
