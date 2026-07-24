import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.repositories.job_repository import JobRepository
from backend.repositories.candidate_repository import CandidateRepository
from backend.models.job import Job

class JobService:
    def __init__(self):
        self.repo = JobRepository()
        self.cand_repo = CandidateRepository()

    async def create_job(self, data: dict) -> Dict[str, Any]:
        job_id = data.get('id') or f"JOB-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        data['id'] = job_id
        job = Job(**data)
        await self.repo.create(job_id, job)
        return job.model_dump()

    async def list_jobs(self, department: Optional[str] = None) -> List[Dict[str, Any]]:
        jobs = await self.repo.get_all()
        if department:
            jobs = [j for j in jobs if getattr(j, 'department', None) == department]
        
        job_dicts = []
        for j in jobs:
            jd = j.model_dump()
            candidates = await self.cand_repo.get_by_job(jd['id'])
            jd['application_count'] = len(candidates)
            job_dicts.append(jd)
            
        return job_dicts

    async def get_job(self, id: str) -> Optional[Dict[str, Any]]:
        job = await self.repo.get(id)
        return job.model_dump() if job else None

    async def get_candidates(self, job_id: str) -> List[Dict[str, Any]]:
        candidates = await self.cand_repo.get_by_job(job_id)
        # Sort by atsScore descending, defaulting to 0
        sorted_candidates = sorted(candidates, key=lambda c: getattr(c, 'atsScore', 0) or getattr(c, 'overallScore', 0) or 0, reverse=True)
        return [c.model_dump() for c in sorted_candidates]

    async def get_pipeline_view(self, job_id: str) -> Dict[str, List[Dict[str, Any]]]:
        candidates = await self.cand_repo.get_by_job(job_id)
        pipeline = {
            'applied': [],
            'screening': [],
            'matching': [],
            'background_check': [],
            'interviewing': [],
            'decision': []
        }
        for c in candidates:
            stage = getattr(c, 'pipeline_stage', 'applied')
            if stage not in pipeline:
                stage = 'applied'
            pipeline[stage].append(c.model_dump())
        return pipeline
