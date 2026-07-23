import uuid
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from fastapi import WebSocket
from backend.repositories.interview_repository import InterviewRepository
from backend.models.interview import Interview

logger = logging.getLogger(__name__)

class InterviewService:
    def __init__(self):
        self.repo = InterviewRepository()

    async def schedule(self, data: dict) -> Dict[str, Any]:
        intv_id = data.get('id') or str(uuid.uuid4())
        data['id'] = intv_id
        data['status'] = 'scheduled'
        interview = Interview(**data)
        await self.repo.create(intv_id, interview)
        return interview.model_dump()

    async def list_interviews(self, candidate_id: Optional[str] = None) -> List[Dict[str, Any]]:
        interviews = await self.repo.get_all()
        if candidate_id:
            interviews = [i for i in interviews if getattr(i, 'candidate_id', None) == candidate_id]
        return [i.model_dump() for i in interviews]

    async def get_interview(self, id: str) -> Optional[Dict[str, Any]]:
        interview = await self.repo.get(id)
        return interview.model_dump() if interview else None

    async def handle_live_interview(self, id: str, websocket: WebSocket):
        """Handle turn-by-turn AI Recruiter interview session over WebSocket."""
        logger.info(f"Live interview session handler started for {id}")
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    msg = json.loads(data)
                    msg_type = msg.get("type")
                    if msg_type == "message":
                        content = msg.get("content", "")
                        await websocket.send_json({
                            "type": "message",
                            "sender": "interviewer",
                            "content": f"AI Recruiter: Thank you for your answer regarding '{content[:50]}...'. Can you tell me more about your experience?",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                    elif msg_type == "ping":
                        await websocket.send_json({"type": "pong"})
                    else:
                        await websocket.send_json({
                            "type": "message",
                            "sender": "interviewer",
                            "content": "Thank you. Let's continue with the next question.",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "message",
                        "sender": "interviewer",
                        "content": f"AI Recruiter received: {data[:100]}",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
        except Exception as e:
            logger.info(f"Interview WebSocket session closed for {id}: {e}")
