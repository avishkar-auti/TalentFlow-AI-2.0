"""Applications controller — candidate job application endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services.application_service import ApplicationService
from backend.shared.response import success_response, APIResponse

router = APIRouter(tags=["Applications"])


class CreateApplicationRequest(BaseModel):
    candidate_id: str
    job_id: str
    cover_note: Optional[str] = None


@router.post("", response_model=APIResponse)
async def create_application(req: CreateApplicationRequest):
    svc = ApplicationService()
    application = await svc.create_application(req.candidate_id, req.job_id, req.cover_note)
    return success_response(application, "Application submitted successfully")


@router.get("/{id}", response_model=APIResponse)
async def get_application(id: str):
    svc = ApplicationService()
    application = await svc.get_application(id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return success_response(application)
