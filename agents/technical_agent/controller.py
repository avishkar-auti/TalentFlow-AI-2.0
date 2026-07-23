"""FastAPI controller for Technical Agent routes."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from .schemas import TechnicalEvaluationRequest, TechnicalEvaluationResponse
from .service import TechnicalService

router = APIRouter(prefix="/api/v1/technical", tags=["technical"])
service = TechnicalService()

@router.post("/evaluate", response_model=TechnicalEvaluationResponse)
async def evaluate_technical_sync(request: TechnicalEvaluationRequest):
    """Synchronously trigger technical evaluation."""
    response = service.evaluate_technical(request.candidate_id, request.interview_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response

@router.post("/evaluate/async")
async def evaluate_technical_async(request: TechnicalEvaluationRequest, background_tasks: BackgroundTasks):
    """Asynchronously trigger technical evaluation."""
    background_tasks.add_task(service.evaluate_technical, request.candidate_id, request.interview_id)
    return {"message": "Technical evaluation started in the background."}
