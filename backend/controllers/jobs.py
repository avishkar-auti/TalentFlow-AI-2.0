from fastapi import APIRouter, HTTPException
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict
from backend.services.job_service import JobService
from backend.shared.response import success_response, APIResponse

router = APIRouter()

class CreateJobRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    title: str
    department: Optional[str] = "Engineering"
    location: Optional[str] = "Remote"
    type: Optional[str] = "Full-time"
    description: Optional[str] = ""
    requirements: Optional[Any] = None
    status: Optional[str] = "active"

@router.post("", response_model=APIResponse)
async def create_job(req: CreateJobRequest):
    service = JobService()
    job = await service.create_job(req.dict())
    return success_response(job, "Job created successfully")

@router.get("", response_model=APIResponse)
async def list_jobs(department: Optional[str] = None):
    service = JobService()
    jobs = await service.list_jobs(department)
    return success_response(jobs)

@router.get("/{id}", response_model=APIResponse)
async def get_job(id: str):
    service = JobService()
    job = await service.get_job(id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return success_response(job)

@router.get("/{id}/candidates", response_model=APIResponse)
async def get_job_candidates(id: str):
    service = JobService()
    candidates = await service.get_candidates(id)
    return success_response(candidates)

@router.get("/{id}/pipeline", response_model=APIResponse)
async def get_job_pipeline(id: str):
    service = JobService()
    pipeline = await service.get_pipeline_view(id)
    return success_response(pipeline)
