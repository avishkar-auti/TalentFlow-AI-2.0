"""Candidate model — flexible Pydantic schema supporting legacy & modern Firestore structures."""
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict, model_validator

class Candidate(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: Optional[str] = None
    candidateId: Optional[str] = None
    name: str = "Candidate"
    email: str = ""
    phone: Optional[str] = None
    resume_url: Optional[str] = Field(default=None, alias="resumeUrl")
    pipeline_stage: str = Field(default="applied", alias="stage")
    status: str = Field(default="active")
    applied_job_id: Optional[str] = Field(default=None, alias="jobId")
    job_id: Optional[str] = None
    created_at: Optional[Any] = Field(default=None, alias="createdAt")
    updated_at: Optional[Any] = Field(default=None, alias="updatedAt")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Ensure id exists
            doc_id = data.get("id") or data.get("candidateId") or data.get("candidate_id")
            if doc_id:
                data["id"] = doc_id
                data["candidateId"] = doc_id
            
            # Ensure job_id / applied_job_id exists
            job_id = data.get("applied_job_id") or data.get("jobId") or data.get("job_id")
            if job_id:
                data["applied_job_id"] = job_id
                data["job_id"] = job_id
                data["jobId"] = job_id
            
            # Ensure stage exists
            stage = data.get("pipeline_stage") or data.get("stage") or "applied"
            data["pipeline_stage"] = str(stage).lower()
            data["stage"] = str(stage).lower()
        return data
