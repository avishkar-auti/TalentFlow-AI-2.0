import os
import shutil
from pathlib import Path
from typing import Optional, List
from fastapi import UploadFile
from .agent import ResumeAgent
from .schemas import ResumeAnalysisResponse

async def upload_and_analyze(
    candidate_id: str, 
    job_id: Optional[str] = None, 
    file: UploadFile = None, 
    job_requirements: Optional[List[str]] = None
) -> ResumeAnalysisResponse:
    """Handles file upload, saves to temporary storage, and triggers real ResumeAgent processing."""
    
    # Save file locally for PyMuPDF AST extraction
    temp_dir = Path(f"backend/temp/candidate_{candidate_id}")
    temp_dir.mkdir(parents=True, exist_ok=True)
    filename = file.filename if file and file.filename else "resume.pdf"
    file_path = temp_dir / filename
    
    if file and hasattr(file, "file"):
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    # Trigger Agent for AST extraction, Groq/AST parsing, ATS scanning, and Firestore persistence
    agent = ResumeAgent()
    result = await agent.process(
        candidate_id=candidate_id, 
        resume_file_path=str(file_path), 
        job_id=job_id,
        job_requirements=job_requirements
    )
    
    return ResumeAnalysisResponse(
        message="Resume Analysis Complete",
        analysis=result.analysis,
        score=result.score
    )
