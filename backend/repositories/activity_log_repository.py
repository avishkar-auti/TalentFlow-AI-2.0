import uuid
from typing import List, Dict, Any
from datetime import datetime, timezone
from .base_repository import BaseRepository
from backend.models import ActivityLog

class ActivityLogRepository(BaseRepository[ActivityLog]):
    def __init__(self):
        super().__init__('activity_logs', ActivityLog)

    async def log_activity(self, agent_name: str, action: str, details: Any, 
                           candidate_id: str = None, user_id: str = None) -> ActivityLog:
        doc_id = str(uuid.uuid4())
        log = ActivityLog(
            agent_name=agent_name,
            action=action,
            details=details if isinstance(details, dict) else {"info": str(details)},
            candidate_id=candidate_id,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        return await self.create(doc_id, log)

    async def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            logs = await self.query(filters=[], limit=limit)
            logs.sort(key=lambda x: str(getattr(x, "timestamp", "")), reverse=True)
            return [l.model_dump() if hasattr(l, "model_dump") else l for l in logs]
        except Exception:
            return []

    async def get_by_candidate(self, candidate_id: str) -> List[Dict[str, Any]]:
        try:
            logs = await self.query(filters=[('candidateId', '==', candidate_id)])
            logs.sort(key=lambda x: str(getattr(x, "timestamp", "")), reverse=True)
            return [l.model_dump() if hasattr(l, "model_dump") else l for l in logs]
        except Exception:
            return []
