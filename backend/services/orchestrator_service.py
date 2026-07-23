"""Orchestrator service — pipeline state management bridge to the Orchestrator agent."""
from typing import Any, Dict


class OrchestratorService:
    """Bridge service for triggering and querying orchestrator pipeline state."""

    async def advance_pipeline(self, candidate_id: str) -> Dict[str, Any]:
        """Trigger the next pipeline stage for a candidate."""
        try:
            from agents.orchestrator.agent import OrchestratorAgent
            agent = OrchestratorAgent()
            await agent.run_pipeline(candidate_id, job_id=None, from_stage="auto")
            return {
                "status": "advanced",
                "candidate_id": candidate_id,
                "message": "Orchestrator triggered pipeline advance",
            }
        except Exception as exc:
            return {
                "status": "error",
                "candidate_id": candidate_id,
                "message": str(exc),
            }

    async def get_pipeline_state(self, candidate_id: str) -> Dict[str, Any]:
        """Return current orchestrator pipeline state for a candidate."""
        try:
            from backend.repositories.candidate_repository import CandidateRepository
            repo = CandidateRepository()
            candidate = await repo.get(candidate_id)
            if not candidate:
                return {"candidate_id": candidate_id, "state": "not_found", "stage": None}
            return {
                "candidate_id": candidate_id,
                "state": "active",
                "stage": getattr(candidate, "pipeline_stage", "unknown"),
                "status": getattr(candidate, "status", "unknown"),
            }
        except Exception as exc:
            return {
                "candidate_id": candidate_id,
                "state": "error",
                "stage": None,
                "message": str(exc),
            }
