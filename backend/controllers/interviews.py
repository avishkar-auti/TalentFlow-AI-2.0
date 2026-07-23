"""Interviews controller — REST scheduling + live WebSocket session + vision proctoring channel."""
import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from pydantic import BaseModel

from backend.services.interview_service import InterviewService
from backend.shared.response import success_response, APIResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Interviews"])


# ── Request schemas ──────────────────────────────────────────────────────────

class ScheduleInterviewRequest(BaseModel):
    candidate_id: str
    job_id: str
    scheduled_at: str
    type: str = "speech"
    duration_minutes: int = 60


# ── REST Endpoints ────────────────────────────────────────────────────────────

@router.post("", response_model=APIResponse)
async def schedule_interview(req: ScheduleInterviewRequest):
    """Create a new interview slot for a candidate."""
    svc = InterviewService()
    interview = await svc.schedule(req.dict())
    return success_response(interview, "Interview scheduled")


@router.get("", response_model=APIResponse)
async def list_interviews(candidate_id: Optional[str] = None):
    """List all interviews, optionally filtered by candidate."""
    svc = InterviewService()
    interviews = await svc.list_interviews(candidate_id)
    return success_response(interviews)


@router.get("/{id}", response_model=APIResponse)
async def get_interview(id: str):
    """Fetch a single interview record by ID."""
    svc = InterviewService()
    interview = await svc.get_interview(id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return success_response(interview)


# ── WebSocket: Main Interview Session ─────────────────────────────────────────

@router.websocket("/ws/interview/{interview_id}")
async def ws_interview_session(websocket: WebSocket, interview_id: str):
    """
    Live turn-by-turn interview WebSocket session.

    Delegates to InterviewService/Agent for real-time audio/text interaction.
    Messages format: {"type": "audio"|"text"|"ping", "data": "..."}
    """
    await websocket.accept()
    svc = InterviewService()
    logger.info(f"Interview WebSocket opened: {interview_id}")
    try:
        await svc.handle_live_interview(interview_id, websocket)
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from interview session {interview_id}")
    except Exception as exc:
        logger.error(f"WS session error for interview {interview_id}: {exc}")
        try:
            await websocket.close(code=1011)
        except Exception:
            pass


# ── WebSocket: Vision / Proctoring Channel ───────────────────────────────────

@router.websocket("/ws/interview/{interview_id}/vision")
async def ws_vision_proctoring(websocket: WebSocket, interview_id: str):
    """
    Dedicated vision proctoring WebSocket channel.

    The browser sends base64-encoded JPEG frames; the server runs
    OpenCV + MediaPipe analysis (face count, gaze direction, head pose, EAR)
    and streams back objective flag events. Flags are also persisted to Firestore.

    Client → Server message format:
        {"type": "frame", "data": "<base64-jpeg>", "reference_photo": "<base64 optional>"}
        {"type": "ping"}

    Server → Client message format:
        {"type": "vision_result", "face_count": N, "gaze_direction": "...", "flags": [...]}
        {"type": "pong"}
        {"type": "error", "message": "..."}
    """
    await websocket.accept()
    logger.info(f"Vision proctoring WebSocket opened: {interview_id}")

    # Lazy-import vision pipeline to avoid loading OpenCV/MediaPipe at startup
    try:
        from agents.interview_agent.vision import VisionProctoring
        from agents.interview_agent.proctoring_store import ProctoringStore
        proctoring = VisionProctoring()
        store = ProctoringStore(interview_id)
    except ImportError as exc:
        logger.warning(f"Vision dependencies not available: {exc}")
        await websocket.send_json({
            "type": "error",
            "message": "Vision proctoring unavailable — install opencv-python-headless and mediapipe"
        })
        await websocket.close(code=1011)
        return

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
                continue

            msg_type = msg.get("type")

            if msg_type == "frame":
                frame_b64 = msg.get("data", "")
                ref_photo = msg.get("reference_photo")

                if not frame_b64:
                    await websocket.send_json({"type": "error", "message": "No frame data provided"})
                    continue

                result = await proctoring.analyze_frame(frame_b64, ref_photo)

                # Persist any emitted flags to Firestore
                if result.get("flags"):
                    await store.store_flags(result["flags"])

                await websocket.send_json({
                    "type": "vision_result",
                    "face_count": result.get("face_count", 0),
                    "face_detected": result.get("face_detected", False),
                    "gaze_direction": result.get("gaze_direction", "unknown"),
                    "gaze_offset": result.get("gaze_offset", 0.0),
                    "head_pose": result.get("head_pose", {}),
                    "ear_value": result.get("ear_value", 0.0),
                    "flags": result.get("flags", []),
                })

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: '{msg_type}'. Expected 'frame' or 'ping'."
                })

    except WebSocketDisconnect:
        logger.info(f"Vision WebSocket disconnected: {interview_id}")
    except Exception as exc:
        logger.error(f"Vision WebSocket error for {interview_id}: {exc}")
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
