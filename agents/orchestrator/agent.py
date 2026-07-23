import logging
from typing import Any, Dict
from pydantic import BaseModel
from backend.shared.constants import USER_FACING_STATUS_MAP
from backend.repositories.activity_log_repository import ActivityLogRepository
from backend.models.activity import ActivityLog
from .state import PipelineState, PipelineStateRepository
from .workflow import PipelineWorkflow

logger = logging.getLogger(__name__)

class PipelineResult(BaseModel):
    candidate_id: str
    job_id: str
    final_stage: str
    status: str
    errors: list[Dict[str, Any]]

class OrchestratorAgent:
    """Central pipeline controller for TalentFlow-AI."""
    
    def __init__(self):
        self.workflow = PipelineWorkflow()
        self.state_repo = PipelineStateRepository()
        self.activity_repo = ActivityLogRepository()
        
    async def run_pipeline(self, candidate_id: str, job_id: str, from_stage: str = 'applied') -> PipelineResult:
        logger.info(f"Starting pipeline for {candidate_id} on job {job_id} from {from_stage}")
        
        state = await self.state_repo.get_state(candidate_id, job_id)
        if not state:
            state = PipelineState(candidate_id=candidate_id, job_id=job_id, current_stage=from_stage)
            await self.state_repo.save_state(state)
            
        current = state.current_stage
        
        while current not in ['rejected', 'offer', 'decision']:
            try:
                # Execute current stage
                result = await self.workflow.execute_stage(current, state)
                
                # Determine next stage
                next_stage = self.workflow.get_next_stage(current, result)
                
                # Update state
                state.update_stage(next_stage, result)
                await self.state_repo.save_state(state)
                
                # Log activity and update user-facing status
                status_msg = USER_FACING_STATUS_MAP.get(next_stage, "Processing application")
                await self.activity_repo.log_activity(
                    agent_name="orchestrator",
                    action=f"transition_to_{next_stage}",
                    details={"user_facing_status": status_msg},
                    candidate_id=candidate_id
                )
                
                current = next_stage
                
            except Exception as e:
                logger.error(f"Error in pipeline stage {current} for candidate {candidate_id}: {e}")
                state.add_error(current, str(e))
                await self.state_repo.save_state(state)
                break
                
        return PipelineResult(
            candidate_id=candidate_id,
            job_id=job_id,
            final_stage=state.current_stage,
            status="completed" if not state.errors else "failed",
            errors=state.errors
        )
