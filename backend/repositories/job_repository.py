from typing import List
from .base_repository import BaseRepository
from backend.models import Job

class JobRepository(BaseRepository[Job]):
    def __init__(self):
        super().__init__('jobs', Job)

    async def get_by_recruiter(self, recruiter_id: str) -> List[Job]:
        return await self.query(filters=[('recruiterId', '==', recruiter_id)])

    async def get_active_jobs(self) -> List[Job]:
        return await self.query(filters=[('status', '==', 'active')])

    async def search_jobs(self, search_term: str) -> List[Job]:
        # Basic exact match for Firestore; in production we'd use Algolia or ElasticSearch
        return await self.query(filters=[('title', '>=', search_term), ('title', '<=', search_term + '\uf8ff')])

    async def get_job_with_candidates(self, job_id: str) -> tuple[Job, list]:
        job = await self.get(job_id)
        if not job:
            return None, []
        from .candidate_repository import CandidateRepository
        candidate_repo = CandidateRepository()
        candidates = await candidate_repo.get_by_job(job_id)
        return job, candidates
