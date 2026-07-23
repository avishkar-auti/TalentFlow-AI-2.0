"""Service layer for Technical Agent."""
import logging
from .agent import TechnicalAgent
from .schemas import TechnicalEvaluationResponse

logger = logging.getLogger(__name__)

class TechnicalService:
    """Service to handle business logic orchestration for technical evaluation."""
    
    def __init__(self):
        self.agent = TechnicalAgent()
        
    def evaluate_technical(self, candidate_id: str, interview_id: str) -> TechnicalEvaluationResponse:
        """Run the technical agent evaluation."""
        try:
            result = self.agent.process(candidate_id, interview_id)
            return TechnicalEvaluationResponse(
                success=True,
                message="Technical evaluation completed successfully.",
                data=result.model_dump(mode='json')
            )
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return TechnicalEvaluationResponse(
                success=False,
                message=str(e)
            )
        except Exception as e:
            logger.exception("Unexpected error during technical evaluation.")
            return TechnicalEvaluationResponse(
                success=False,
                message="An internal error occurred."
            )
