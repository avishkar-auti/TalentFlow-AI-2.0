from typing import List, Optional, Tuple, Dict, Any
from .base_repository import BaseRepository
from backend.models import Candidate

class CandidateRepository(BaseRepository[Candidate]):
    def __init__(self):
        super().__init__('candidates', Candidate)
    
    async def get_by_email(self, email: str) -> Optional[Candidate]:
        results = await self.query(filters=[('email', '==', email)], limit=1)
        return results[0] if results else None
    
    async def get_by_job(self, job_id: str) -> List[Candidate]:
        return await self.query(filters=[('jobId', '==', job_id)])
    
    async def get_by_stage(self, stage: str) -> List[Candidate]:
        return await self.query(filters=[('stage', '==', stage)])
    
    async def get_pipeline_counts(self) -> Dict[str, int]:
        counts = {}
        # In a real app we might aggregate, but for Firestore we can count each stage, or fetch all and count
        stages = ['applied', 'screening', 'interview', 'offer', 'hired', 'rejected']
        for stage in stages:
            counts[stage] = await self.count([('stage', '==', stage)])
        return counts

    async def move_to_stage(self, candidate_id: str, new_stage: str) -> Candidate:
        return await self.update(candidate_id, {'stage': new_stage})

    async def get_with_analysis(self, candidate_id: str) -> Optional[Tuple[Candidate, Optional[Dict[str, Any]]]]:
        candidate = await self.get(candidate_id)
        if not candidate:
            return None
        analysis = await self.get_subcollection(candidate_id, 'resume_analysis', 'latest')
        return candidate, analysis
