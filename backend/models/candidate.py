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
    job_title: Optional[str] = Field(default=None, alias="jobTitle")
    ats_score: Optional[float] = Field(default=None, alias="atsScore")
    atsScore: Optional[float] = None
    overallScore: Optional[float] = None
    overallMatch: Optional[float] = None
    skills: Any = Field(default_factory=list)
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
            stage = data.get("pipeline_stage") or data.get("stage") or data.get("pipelineStage") or "applied"
            data["pipeline_stage"] = str(stage).lower()
            data["stage"] = str(stage).lower()
            data["pipelineStage"] = str(stage).lower()

            # Ensure ATS and Match scores are synced across alias forms
            score_val = data.get("overallScore") or data.get("atsScore") or data.get("overallMatch") or data.get("ats_score")
            if score_val is not None:
                try:
                    f_val = float(score_val)
                    data["ats_score"] = f_val
                    data["atsScore"] = f_val
                    data["overallScore"] = f_val
                    data["overallMatch"] = f_val
                except (ValueError, TypeError):
                    pass
        return data

