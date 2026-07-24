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


class UpdateInterviewRequest(BaseModel):
    candidate_id: Optional[str] = None
    job_id: Optional[str] = None
    scheduled_at: Optional[str] = None
    type: Optional[str] = None
    duration_minutes: Optional[int] = None


@router.put("/{id}", response_model=APIResponse)
async def update_interview(id: str, req: UpdateInterviewRequest):
    """Edit/reschedule an existing interview (partial update)."""
    svc = InterviewService()
    existing = await svc.get_interview(id)
    if not existing:
        raise HTTPException(status_code=404, detail="Interview not found")
    updates = {k: v for k, v in req.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")
    result = await svc.update_interview(id, updates)
    return success_response(result, "Interview updated")


@router.delete("/{id}", response_model=APIResponse)
async def delete_interview(id: str):
    """Cancel/remove a scheduled interview."""
    svc = InterviewService()
    existing = await svc.get_interview(id)
    if not existing:
        raise HTTPException(status_code=404, detail="Interview not found")
    await svc.delete_interview(id)
    return success_response({"id": id}, "Interview cancelled")


@router.post("/{id}/pass", response_model=APIResponse)
async def pass_interview(id: str, notes: str = ''):
    svc = InterviewService()
    result = await svc.pass_interview(id, notes)
    return success_response(result, 'Interview marked as passed')

@router.post("/{id}/fail", response_model=APIResponse) 
async def fail_interview(id: str, notes: str = ''):
    svc = InterviewService()
    result = await svc.fail_interview(id, notes)
    return success_response(result, 'Interview marked as failed')

@router.get("/candidate/{candidate_id}/scheduled", response_model=APIResponse)
async def get_candidate_interviews(candidate_id: str):
    svc = InterviewService()
    interviews = await svc.get_candidate_scheduled_interviews(candidate_id)
    return success_response(interviews)


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

                flags = result.get("flags", [])

                # Persist any emitted flags to Firestore
                if flags:
                    await store.store_flags(flags)

                warning_count = proctoring.flag_tracker.warning_count
                has_termination_flag = any(f.get("is_terminated") for f in flags) or warning_count >= 5

                await websocket.send_json({
                    "type": "vision_result",
                    "face_count": result.get("face_count", 0),
                    "face_detected": result.get("face_detected", False),
                    "gaze_direction": result.get("gaze_direction", "unknown"),
                    "gaze_offset": result.get("gaze_offset", 0.0),
                    "head_pose": result.get("head_pose", {}),
                    "ear_value": result.get("ear_value", 0.0),
                    "warning_count": warning_count,
                    "max_warnings": proctoring.flag_tracker.max_warnings,
                    "flags": flags,
                    "is_terminated": has_termination_flag
                })

                if has_termination_flag:
                    logger.warning(f"Interview {interview_id} terminated due to 5 proctoring warnings.")
                    try:
                        import firebase_admin.firestore
                        from datetime import datetime, timezone
                        db = firebase_admin.firestore.client()
                        db.collection("interviews").document(interview_id).update({
                            "status": "terminated",
                            "termination_reason": "Maximum proctoring warnings (5/5) exceeded.",
                            "ended_at": datetime.now(timezone.utc).isoformat(),
                        })
                    except Exception as e:
                        logger.error(f"Error updating terminated status in Firestore: {e}")

                    await websocket.send_json({
                        "type": "interview_terminated",
                        "reason": "Interview automatically terminated. Maximum warning limit (5/5) reached for proctoring violations.",
                        "warning_count": warning_count
                    })
                    break

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


# In-memory connection pool for 1-on-1 chat + WebRTC signaling
chat_connections: dict = {}  # interview_id -> {recruiter: ws, candidate: ws}

@router.websocket('/ws/recruiter-chat/{interview_id}')
async def ws_recruiter_chat(websocket: WebSocket, interview_id: str, role: str = 'candidate'):
    """1-on-1 recruiter <-> candidate chat + WebRTC signaling relay for the live meeting room."""
    await websocket.accept()
    if interview_id not in chat_connections:
        chat_connections[interview_id] = {}
    chat_connections[interview_id][role] = websocket

    other_role = 'candidate' if role == 'recruiter' else 'recruiter'
    other_ws = chat_connections.get(interview_id, {}).get(other_role)
    # Let the other party know a peer has (re)joined so they can (re)start the WebRTC offer.
    if other_ws:
        try:
            await other_ws.send_text(json.dumps({'type': 'peer_joined', 'role': role}))
        except Exception:
            pass

    try:
        import firebase_admin.firestore
        from datetime import datetime, timezone
        db = firebase_admin.firestore.client()
        
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)

                # WebRTC signaling (offer/answer/ice-candidate) — just relay to the other
                # party untouched, no persistence needed for signaling payloads.
                if msg.get('type') in ('webrtc_offer', 'webrtc_answer', 'webrtc_ice'):
                    other_ws = chat_connections.get(interview_id, {}).get(other_role)
                    if other_ws:
                        try:
                            await other_ws.send_text(json.dumps({**msg, 'sender_role': role}))
                        except Exception:
                            pass
                    continue

                content = msg.get('content', '')
                timestamp = datetime.now(timezone.utc).isoformat()
                
                # Persist to Firestore
                db.collection('interviews').document(interview_id).collection('chat').document().set({
                    'sender_role': role,
                    'content': content,
                    'timestamp': timestamp,
                    'interview_id': interview_id
                })
                
                # Relay to the other party
                other_ws = chat_connections.get(interview_id, {}).get(other_role)
                
                relay_msg = json.dumps({
                    'type': 'chat_message',
                    'sender_role': role,
                    'content': content,
                    'timestamp': timestamp
                })
                
                if other_ws:
                    try:
                        await other_ws.send_text(relay_msg)
                    except Exception:
                        pass
                        
                # Echo back to sender as confirmation
                await websocket.send_text(json.dumps({'type': 'sent', 'timestamp': timestamp}))
                    
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        if interview_id in chat_connections:
            chat_connections[interview_id].pop(role, None)
            # Tell the other party we left so they can tear down their peer connection.
            remaining_ws = chat_connections.get(interview_id, {}).get(other_role)
            if remaining_ws:
                try:
                    await remaining_ws.send_text(json.dumps({'type': 'peer_left', 'role': role}))
                except Exception:
                    pass



# ── Code Submission & Scoring ────────────────────────────────────────────────

class CodeSubmissionRequest(BaseModel):
    interview_id: str
    language: str
    code: str
    expected_output: str = ""

@router.post("/code-submission", response_model=APIResponse)
async def submit_code(req: CodeSubmissionRequest):
    """Score submitted code from technical interview."""
    from backend.services.interview_manager import InterviewManager
    manager = InterviewManager()

    score_data = await manager.score_code_submission(req.code, req.language, req.expected_output)

    import firebase_admin.firestore
    db = firebase_admin.firestore.client()
    db.collection('interviews').document(req.interview_id).update({
        'code_submission': {
            'language': req.language,
            'code': req.code,
            'score': score_data['code_quality_score'],
            'submitted_at': datetime.now(timezone.utc).isoformat()
        }
    })

    return success_response(score_data, "Code scored successfully")


# ── Interview Summary ────────────────────────────────────────────────────────

@router.get("/{interview_id}/summary", response_model=APIResponse)
async def get_interview_summary(interview_id: str):
    """Get complete interview summary with chat history and proctoring flags."""
    from backend.services.interview_manager import InterviewManager
    manager = InterviewManager()

    summary = await manager.get_interview_summary(interview_id)
    if not summary.get('interview'):
        raise HTTPException(status_code=404, detail="Interview not found")

    return success_response(summary, "Interview summary retrieved")


# ── Proctoring Flag Recording ────────────────────────────────────────────────

class ProctoringFlagRequest(BaseModel):
    interview_id: str
    flag_type: str
    severity: str = "warning"

@router.post("/proctoring-flag", response_model=APIResponse)
async def record_proctoring_flag(req: ProctoringFlagRequest):
    """Record proctoring violation. Auto-terminates on 5th warning."""
    from backend.services.interview_manager import InterviewManager
    manager = InterviewManager()

    result = await manager.add_proctoring_flag(req.interview_id, req.flag_type, req.severity)

    if result.get('auto_terminated'):
        return success_response(result, "Interview auto-terminated due to excessive violations", status_code=400)

    return success_response(result, "Proctoring flag recorded")


# ── Offer Management ────────────────────────────────────────────────────────

class OfferRequest(BaseModel):
    candidate_id: str
    job_id: str
    salary: str
    start_date: str
    notes: str = ""

@router.post("/offer/generate", response_model=APIResponse)
async def generate_offer(req: OfferRequest):
    """Generate and send offer letter"""
    from backend.services.offer_service import OfferService
    svc = OfferService()
    result = await svc.generate_offer(req.candidate_id, req.job_id, req.salary, req.start_date, req.notes)
    return success_response(result, "Offer sent successfully")

@router.get("/offer/{candidate_id}", response_model=APIResponse)
async def get_offer(candidate_id: str):
    """Get candidate's offer"""
    from backend.services.offer_service import OfferService
    svc = OfferService()
    offer = await svc.get_offer(candidate_id)
    if not offer:
        raise HTTPException(status_code=404, detail="No offer found")
    return success_response(offer)

@router.post("/offer/{candidate_id}/accept", response_model=APIResponse)
async def accept_offer(candidate_id: str):
    """Candidate accepts offer"""
    from backend.services.offer_service import OfferService
    svc = OfferService()
    result = await svc.accept_offer(candidate_id)
    return success_response(result, "Offer accepted successfully")

@router.post("/offer/{candidate_id}/reject", response_model=APIResponse)
async def reject_offer(candidate_id: str, reason: str = ""):
    """Candidate rejects offer"""
    from backend.services.offer_service import OfferService
    svc = OfferService()
    result = await svc.reject_offer(candidate_id, reason)
    return success_response(result, "Offer rejected")


from datetime import timezone


# ── Background Verification ────────────────────────────────────────────────

@router.post("/background-check/initiate/{candidate_id}", response_model=APIResponse)
async def initiate_background_check(candidate_id: str):
    """Initiate background verification for candidate"""
    from backend.services.background_check_service import BackgroundCheckService
    svc = BackgroundCheckService()
    result = await svc.initiate_background_check(candidate_id)
    return success_response(result, "Background check initiated")

@router.get("/background-check/{candidate_id}", response_model=APIResponse)
async def get_background_status(candidate_id: str):
    """Get background check status"""
    from backend.services.background_check_service import BackgroundCheckService
    svc = BackgroundCheckService()
    result = await svc.get_background_status(candidate_id)
    return success_response(result)



# ── Activity Tracking ────────────────────────────────────────────────────────

@router.get("/activity/recent", response_model=APIResponse)
async def get_recent_activities(limit: int = 10):
    """Get recent hiring activities for dashboard"""
    from backend.services.activity_logger import ActivityLogger
    activities = await ActivityLogger.get_recent_activities(limit)
    return success_response(activities, "Recent activities retrieved")

