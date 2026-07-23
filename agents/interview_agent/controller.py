from fastapi import APIRouter, HTTPException, WebSocket, Depends
from typing import Dict, Any

from .schemas import InterviewStartRequest, InterviewStartResponse, InterviewStatusResponse, TranscriptResponse, ProctoringResponse
from .service import InterviewService
from .session import InterviewSessionManager

router = APIRouter(prefix="/api/v1/interviews", tags=["Interviews"])
ws_router = APIRouter(tags=["WebSockets"])

service = InterviewService()
session_manager = InterviewSessionManager()

@router.post("/{interview_id}/start", response_model=InterviewStartResponse)
async def start_interview(interview_id: str, request: InterviewStartRequest):
    return await service.create_interview(request)

@router.get("/{interview_id}/status")
async def get_status(interview_id: str):
    status = await service.get_session_status(interview_id)
    if not status:
        raise HTTPException(status_code=404, detail="Interview not found")
    return status

@router.get("/{interview_id}/transcript")
async def get_transcript(interview_id: str):
    session = await service.repo.get_session(interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    return TranscriptResponse(interview_id=interview_id, turns=[turn.dict() for turn in session.turns])

@router.get("/{interview_id}/proctoring")
async def get_proctoring(interview_id: str):
    session = await service.repo.get_session(interview_id)
    if not session:
         raise HTTPException(status_code=404, detail="Interview not found")
    return ProctoringResponse(interview_id=interview_id, flags=[f.dict() for f in session.proctoring.flags])

@ws_router.websocket("/ws/interview/{interview_id}")
async def websocket_endpoint(websocket: WebSocket, interview_id: str):
    await session_manager.handle_websocket(websocket, interview_id)
