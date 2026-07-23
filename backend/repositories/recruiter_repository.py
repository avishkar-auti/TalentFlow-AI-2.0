from typing import Optional, Dict
from .base_repository import BaseRepository
from backend.models import Recruiter

class RecruiterRepository(BaseRepository[Recruiter]):
    def __init__(self):
        super().__init__('recruiters', Recruiter)

    async def get_by_email(self, email: str) -> Optional[Recruiter]:
        results = await self.query(filters=[('email', '==', email)], limit=1)
        return results[0] if results else None
    
    async def get_dashboard_stats(self, recruiter_id: str) -> Dict[str, int]:
        from .job_repository import JobRepository
        from .candidate_repository import CandidateRepository
        
        job_repo = JobRepository()
        candidate_repo = CandidateRepository()
        
        active_jobs = await job_repo.count([('recruiterId', '==', recruiter_id), ('status', '==', 'active')])
        # Assuming candidates have recruiterId or we count based on jobs. 
        # For simplicity, returning just active jobs count here, but can be expanded.
        
        return {
            'active_jobs': active_jobs,
            # Add more stats here as needed
        }
