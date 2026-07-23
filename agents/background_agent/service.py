from .agent import BackgroundAgent
from .models import BackgroundCheckResult

class BackgroundService:
    def __init__(self):
        self.agent = BackgroundAgent()

    async def run_background_check(self, candidate_id: str, job_id: str) -> BackgroundCheckResult:
        """Executes the background check for a candidate."""
        return await self.agent.process(candidate_id, job_id)

background_service = BackgroundService()
