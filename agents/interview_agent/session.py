import logging
import json
import asyncio
from typing import Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

from .models import InterviewSession, InterviewPhase, SessionStatus, ProctoringFlag, ProctoringFlagType
from .agent import InterviewAgent
from .vision import VisionProctoring
from .firebase import InterviewRepository

logger = logging.getLogger(__name__)

class InterviewSessionManager:
    def __init__(self):
        self.active_sessions: Dict[str, WebSocket] = {}
        self.agent = InterviewAgent()
        self.vision = VisionProctoring()
        self.repo = InterviewRepository()

    async def handle_websocket(self, ws: WebSocket, interview_id: str):
        await ws.accept()
        self.active_sessions[interview_id] = ws
        
        # Load session
        session = await self.repo.get_session(interview_id)
        if not session:
            await ws.send_json({"type": "error", "message": "Session not found."})
            await ws.close()
            return
            
        session.status = SessionStatus.IN_PROGRESS
        await self.repo.save_session(session)

        try:
            while True:
                data = await ws.receive_text()
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "consent_accepted":
                    session.current_phase = InterviewPhase.INTRO
                    await self.repo.save_session(session)
                    await ws.send_json({"type": "session_status", "phase": session.current_phase.value})
                    
                    # Trigger first interviewer greeting
                    response = await self.agent.process_turn(session, "[Candidate provided consent and is ready to start.]")
                    await ws.send_json({"type": "interviewer_text", "message": response.message})
                    await self.repo.save_session(session)
                    
                elif msg_type == "text_input":
                    candidate_text = message.get("text", "")
                    if session.current_phase != InterviewPhase.CONSENT:
                        response = await self.agent.process_turn(session, candidate_text)
                        
                        if response.next_phase:
                            session.current_phase = response.next_phase
                            
                        await ws.send_json({
                            "type": "interviewer_text", 
                            "message": response.message,
                            "phase": session.current_phase.value
                        })
                        await self.repo.save_session(session)
                        
                elif msg_type == "video_frame":
                    # Process frame asynchronously without blocking the loop
                    frame_data = message.get("frame") # Assuming base64 or bytes
                    if frame_data:
                        asyncio.create_task(self._process_video_frame(session, ws, frame_data))
                        
                elif msg_type == "tab_switch":
                    flag = ProctoringFlag(
                        flag_type=ProctoringFlagType.TAB_SWITCH,
                        description="Candidate switched browser tabs.",
                        severity="high"
                    )
                    session.proctoring.flags.append(flag)
                    await self.repo.save_session(session)
                    await ws.send_json({"type": "proctoring_flag", "flag": flag.dict()})
                    
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for session {interview_id}")
            self.active_sessions.pop(interview_id, None)
            
        except Exception as e:
            logger.error(f"Error in websocket loop: {e}")
            await ws.close()
            
    async def _process_video_frame(self, session: InterviewSession, ws: WebSocket, frame_data: Any):
        try:
            flags = await self.vision.analyze_frame(frame_data)
            if flags:
                session.proctoring.flags.extend(flags)
                # Save flags to repo
                await self.repo.save_session(session)
                # Optionally notify client
                for flag in flags:
                    await ws.send_json({"type": "proctoring_flag", "flag": flag.dict()})
        except Exception as e:
            logger.error(f"Error processing video frame: {e}")
