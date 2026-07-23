"""Recruiters controller — recruiter account management (admin-gated)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services.recruiter_service import RecruiterService
from backend.shared.response import success_response, APIResponse

router = APIRouter(tags=["Recruiters"])


class CreateRecruiterRequest(BaseModel):
    name: str
    email: str
    role: str = "recruiter"


class UpdateRoleRequest(BaseModel):
    role: str


@router.get("", response_model=APIResponse)
async def list_recruiters():
    svc = RecruiterService()
    recruiters = await svc.list_recruiters()
    return success_response(recruiters)


@router.post("", response_model=APIResponse)
async def create_recruiter(req: CreateRecruiterRequest):
    svc = RecruiterService()
    recruiter = await svc.create_recruiter(req.name, req.email, req.role)
    return success_response(recruiter, "Recruiter created")


@router.patch("/{id}/role", response_model=APIResponse)
async def update_role(id: str, req: UpdateRoleRequest):
    svc = RecruiterService()
    result = await svc.update_role(id, req.role)
    return success_response(result, f"Role updated to {req.role}")
