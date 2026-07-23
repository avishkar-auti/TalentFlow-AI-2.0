"""
Health Controller API Endpoints.
"""
from fastapi import APIRouter
from backend.shared.response import success_response

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    return success_response(data={"status": "healthy", "service": "TalentFlow-AI Engine"}, message="Service is operational.")
