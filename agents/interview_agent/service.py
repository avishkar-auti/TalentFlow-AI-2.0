import logging
import uuid
from typing import Optional, List, Dict, Any

from .models import InterviewSession, SessionStatus
from .schemas import InterviewStartRequest, InterviewStartResponse
from .agent import InterviewAgent
from .firebase import InterviewRepository

logger = logging.getLogger(__name__)

class InterviewService:
    def __init__(self):
        self.agent = InterviewAgent()
        self.repo = InterviewRepository()

    async def create_interview(self, request: InterviewStartRequest) -> InterviewStartResponse:
        interview_id = str(uuid.uuid4())
        session = await self.agent.start_session(
            interview_id=interview_id,
            candidate_id=request.candidate_id,
            job_id=request.job_id
        )
        await self.repo.save_session(session)
        
        ws_url = f"ws://localhost:8000/ws/interview/{interview_id}" # Example URL
        
        return InterviewStartResponse(
            interview_id=interview_id,
            ws_url=ws_url,
            status=session.status
        )
        
    async def get_session_status(self, interview_id: str) -> Optional[Dict[str, Any]]:
        session = await self.repo.get_session(interview_id)
        if not session:
            return None
        return {
            "interview_id": session.interview_id,
            "status": session.status,
            "current_phase": session.current_phase,
            "start_time": session.start_time
        }
