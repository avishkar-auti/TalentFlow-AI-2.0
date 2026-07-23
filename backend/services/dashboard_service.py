from typing import Dict, Any, List
from backend.repositories.candidate_repository import CandidateRepository
from backend.repositories.job_repository import JobRepository
from backend.repositories.interview_repository import InterviewRepository
from backend.repositories.activity_log_repository import ActivityLogRepository

class DashboardService:
    def __init__(self):
        self.cand_repo = CandidateRepository()
        self.job_repo = JobRepository()
        self.int_repo = InterviewRepository()
        self.act_repo = ActivityLogRepository()

    async def get_overall_stats(self) -> Dict[str, int]:
        cands = await self.cand_repo.get_all()
        jobs = await self.job_repo.get_all()
        interviews = await self.int_repo.get_all()
        
        hired = [c for c in cands if getattr(c, "pipeline_stage", "") == "hired"]
        
        return {
            "total_candidates": len(cands),
            "open_jobs": len(jobs),
            "interviews_scheduled": len([i for i in interviews if getattr(i, "status", "") == "scheduled"]),
            "hired_count": len(hired)
        }

    async def get_pipeline_counts(self) -> Dict[str, int]:
        cands = await self.cand_repo.get_all()
        counts = {
            "applied": 0, "screening": 0, "recruiter_review": 0,
            "interview_scheduled": 0, "interview_completed": 0,
            "decision": 0, "hired": 0, "rejected": 0
        }
        for c in cands:
            stage = getattr(c, "pipeline_stage", "applied")
            if stage in counts:
                counts[stage] += 1
            else:
                counts["applied"] += 1
        return counts

    async def get_recent_activity(self, limit: int = 20) -> List[Dict[str, Any]]:
        activities = await self.act_repo.get_recent(limit)
        return [a.model_dump() for a in activities]
