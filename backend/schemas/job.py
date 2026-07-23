"""Job schemas."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ..models.job import JobRequirements, Job

class CreateJobRequest(BaseModel):
    title: str
    description: str
    requirements: JobRequirements
    recruiter_id: str

class UpdateJobRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[JobRequirements] = None
    status: Optional[str] = None

class JobResponse(BaseModel):
    id: str
    title: str
    description: str
    requirements: JobRequirements
    recruiter_id: str
    status: str
    created_at: datetime
    application_count: int
    pipeline_stages: List[str]

class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    size: int
