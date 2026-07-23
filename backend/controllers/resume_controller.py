"""
Resume Controller API Endpoints.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from agents.resume_agent.service import upload_and_analyze
from backend.shared.response import success_response, APIResponse

router = APIRouter(prefix="/resume", tags=["Resume Agent"])

@router.post("/upload")
async def upload_resume_endpoint(
    candidate_id: str = Form(...),
    job_id: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    try:
        res = await upload_and_analyze(candidate_id=candidate_id, job_id=job_id, file=file)
        return success_response(data=res.model_dump(), message="Resume AST scanning & analysis complete.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
