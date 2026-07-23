from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from .schemas import DecisionRequest, DecisionResponse
from .service import DecisionService

router = APIRouter(prefix="/decision", tags=["Decision"])
service = DecisionService()

@router.post("/", response_model=DecisionResponse)
def make_decision(request: DecisionRequest):
    try:
        return service.process_decision(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{candidate_id}/report")
def get_report_pdf(candidate_id: str):
    file_path = f"report_{candidate_id}.pdf"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf", filename=file_path)
    raise HTTPException(status_code=404, detail="Report not found")
