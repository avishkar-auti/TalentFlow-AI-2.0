from typing import List
from .base_repository import BaseRepository
from backend.models import Report

class ReportRepository(BaseRepository[Report]):
    def __init__(self):
        super().__init__('reports', Report)

    async def get_by_candidate(self, candidate_id: str) -> List[Report]:
        return await self.query(filters=[('candidateId', '==', candidate_id)])

    async def get_by_job(self, job_id: str) -> List[Report]:
        return await self.query(filters=[('jobId', '==', job_id)])
