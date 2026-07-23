from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import Optional
from .service import upload_and_analyze
from .schemas import ResumeAnalysisResponse
from .firebase import get_analysis

# Dummy auth dependency for structure. Replace with real dependency.
def get_current_user():
    return {"user_id": "system"}

router = APIRouter(prefix="/api/v1/candidates", tags=["Resumes"])

@router.post("/{candidate_id}/resume", response_model=ResumeAnalysisResponse)
async def upload_resume(
    candidate_id: str,
    job_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Uploads a resume and runs analysis."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        # In a real scenario, we might fetch job_requirements using job_id from DB
        job_requirements = [] 
        response = await upload_and_analyze(candidate_id, job_id, file, job_requirements)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{candidate_id}/resume/analysis")
async def get_resume_analysis(
    candidate_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Retrieves the latest resume analysis for a candidate."""
    try:
        data = await get_analysis(candidate_id)
        if not data:
            raise HTTPException(status_code=404, detail="Analysis not found.")
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
