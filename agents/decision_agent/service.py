from .agent import DecisionAgent
from .schemas import DecisionRequest, DecisionResponse

class DecisionService:
    def __init__(self):
        self.agent = DecisionAgent()
        
    def process_decision(self, request: DecisionRequest) -> DecisionResponse:
        result = self.agent.process(request.candidate_id, request.job_id)
        return DecisionResponse(success=True, data=result)
