from typing import List
from .base_repository import BaseRepository
from backend.models import Application

class ApplicationRepository(BaseRepository[Application]):
    def __init__(self):
        super().__init__('applications', Application)
        
    async def get_by_job(self, job_id: str) -> List[Application]:
        return await self.query(filters=[('jobId', '==', job_id)])
        
    async def get_by_candidate(self, candidate_id: str) -> List[Application]:
        return await self.query(filters=[('candidateId', '==', candidate_id)])
