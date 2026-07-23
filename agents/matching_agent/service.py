import logging
from .agent import MatchingAgent
from .schemas import MatchResponse
from .models import MatchingResult

logger = logging.getLogger(__name__)

async def run_matching(candidate_id: str, job_id: str) -> MatchResponse:
    try:
        agent = MatchingAgent()
        result = await agent.process(candidate_id, job_id)
        return MatchResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Error running matching for {candidate_id} and {job_id}: {e}")
        return MatchResponse(success=False, data=None, error=str(e))
