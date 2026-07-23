"""Candidate schemas."""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..shared.enums import PipelineStage, CandidateStatus
from ..models.candidate import Candidate

class CreateCandidateRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    applied_job_id: str

class UpdateCandidateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    pipeline_stage: Optional[PipelineStage] = None
    status: Optional[CandidateStatus] = None

class CandidateResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    pipeline_stage: PipelineStage
    status: CandidateStatus
    applied_job_id: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

class CandidateListResponse(BaseModel):
    candidates: List[CandidateResponse]
    total: int
    page: int
    size: int

class CandidatePipelineResponse(BaseModel):
    pipeline_stage: PipelineStage
    status: CandidateStatus
    updated_at: datetime
