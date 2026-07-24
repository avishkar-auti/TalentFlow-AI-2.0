"""Interview model — enhanced with round system and chat for TalentFlow-AI-2.0."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any


class Interview(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: Optional[str] = None
    candidate_id: Optional[str] = Field(default=None, alias="candidateId")
    job_id: Optional[str] = Field(default=None, alias="jobId")
    scheduled_at: Optional[Any] = Field(default=None, alias="scheduledAt")
    duration_minutes: int = Field(default=45, alias="durationMinutes")
    status: str = "scheduled"

    # Interview round system
    type: str = "ai_screening"               # ai_screening | hr_round | technical_coding
    interview_round: str = "ai_screening"    # same as type, kept for clarity
    round_number: int = 1                    # 1=AI, 2=HR, 3=Technical

    # Meet link for candidates to join
    meet_link: Optional[str] = Field(default=None, alias="meetLink")

    # Pass/fail result
    pass_fail: Optional[str] = Field(default=None, alias="passFail")   # pass | fail
    result_notes: Optional[str] = Field(default=None, alias="resultNotes")
    next_round_id: Optional[str] = Field(default=None, alias="nextRoundId")

    # Proctoring
    proctoringFlags: List[Any] = Field(default_factory=list)
    interviewerType: str = "ai_gemini"

    # Metadata
    termination_reason: Optional[str] = Field(default=None, alias="terminationReason")
    ended_at: Optional[Any] = Field(default=None, alias="endedAt")
    created_at: Optional[Any] = Field(default=None, alias="createdAt")
    updated_at: Optional[Any] = Field(default=None, alias="updatedAt")
