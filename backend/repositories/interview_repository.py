from typing import List
from datetime import datetime
from .base_repository import BaseRepository
from backend.models import Interview

class InterviewRepository(BaseRepository[Interview]):
    def __init__(self):
        super().__init__('interviews', Interview)

    async def get_by_candidate(self, candidate_id: str) -> List[Interview]:
        return await self.query(filters=[('candidateId', '==', candidate_id)])

    async def get_scheduled(self) -> List[Interview]:
        return await self.query(filters=[('status', '==', 'scheduled')])

    async def get_completed(self) -> List[Interview]:
        return await self.query(filters=[('status', '==', 'completed')])

    async def get_upcoming(self, limit: int = 10) -> List[Interview]:
        now = datetime.utcnow().isoformat()
        return await self.query(
            filters=[('scheduledAt', '>=', now), ('status', '==', 'scheduled')],
            order_by='scheduledAt',
            direction='ASCENDING',
            limit=limit
        )
