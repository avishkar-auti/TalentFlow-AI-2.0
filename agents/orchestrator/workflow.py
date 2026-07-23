import asyncio
import logging
from typing import Any, Callable, Dict, List
from .state import PipelineState
from .router import AgentRouter

logger = logging.getLogger(__name__)

class PipelineWorkflow:
    """Defines the workflow transitions for the pipeline."""
    
    # State machine definition
    TRANSITIONS = {
        'applied': ['screening'],
        'screening': ['matching', 'rejected'],
        'matching': ['background_check', 'rejected'],
        'background_check': ['interview_wait', 'rejected'],
        'interview_wait': ['interviewing'],
        'interviewing': ['decision'],
        'decision': ['offer', 'rejected']
    }
    
    def __init__(self):
        self.router = AgentRouter()
        
    def get_next_stage(self, current_stage: str, result: Dict[str, Any]) -> str:
        if result.get('status') == 'rejected':
            return 'rejected'
            
        allowed = self.TRANSITIONS.get(current_stage, [])
        # For simplicity, default to the first allowed non-rejected stage if successful
        for stage in allowed:
            if stage != 'rejected':
                return stage
        return current_stage
        
    async def execute_stage(self, stage: str, state: PipelineState) -> Dict[str, Any]:
        logger.info(f"Executing stage {stage} for candidate {state.candidate_id}")
        
        # Parallel execution for interviews
        if stage == 'interviewing':
            return await self._run_parallel_interviews(state)
            
        agent = self.router.get_agent_for_stage(stage)
        if not agent:
            logger.warning(f"No agent found for stage {stage}, skipping execution")
            return {"status": "success", "message": "Manual review required"}
            
        try:
            # Assuming agents have an async process method
            result = await agent.process(candidate_id=state.candidate_id, job_id=state.job_id)
            return result
        except Exception as e:
            logger.error(f"Error in stage {stage}: {str(e)}")
            raise

    async def _run_parallel_interviews(self, state: PipelineState) -> Dict[str, Any]:
        """Runs Speech and Technical interviews in parallel"""
        # This would call interview agents via router or specific logic
        # Placeholder for parallel execution
        # results = await asyncio.gather(
        #     self.router.get_agent_for_stage('interview_speech').process(state.candidate_id),
        #     self.router.get_agent_for_stage('interview_technical').process(state.candidate_id)
        # )
        await asyncio.sleep(0.1) # Simulate work
        return {"status": "success", "speech": "passed", "technical": "passed"}
