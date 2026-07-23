"""FastAPI controller for Speech Agent routes."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from .schemas import SpeechAnalysisRequest, SpeechAnalysisResponse
from .service import SpeechService

router = APIRouter(prefix="/api/v1/speech", tags=["speech"])
service = SpeechService()

@router.post("/analyze", response_model=SpeechAnalysisResponse)
async def analyze_speech_sync(request: SpeechAnalysisRequest):
    """
    Synchronously trigger speech analysis for a given interview.
    """
    response = service.analyze_speech(request.candidate_id, request.interview_id)
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    return response

@router.post("/analyze/async")
async def analyze_speech_async(request: SpeechAnalysisRequest, background_tasks: BackgroundTasks):
    """
    Asynchronously trigger speech analysis.
    """
    background_tasks.add_task(service.analyze_speech, request.candidate_id, request.interview_id)
    return {"message": "Speech analysis started in the background."}
