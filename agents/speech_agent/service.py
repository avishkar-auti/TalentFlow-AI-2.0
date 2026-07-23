"""Service layer for Speech Agent."""
import logging
from .agent import SpeechAgent
from .schemas import SpeechAnalysisResponse

logger = logging.getLogger(__name__)

class SpeechService:
    """Service to handle business logic orchestration for speech analysis."""
    
    def __init__(self):
        self.agent = SpeechAgent()
        
    def analyze_speech(self, candidate_id: str, interview_id: str) -> SpeechAnalysisResponse:
        """
        Run the speech agent analysis for a candidate's interview.
        
        Args:
            candidate_id: The ID of the candidate.
            interview_id: The ID of the interview.
            
        Returns:
            SpeechAnalysisResponse indicating success or failure with data.
        """
        try:
            result = self.agent.process(candidate_id, interview_id)
            return SpeechAnalysisResponse(
                success=True,
                message="Speech analysis completed successfully.",
                data=result.model_dump(mode='json')
            )
        except ValueError as e:
            logger.error(f"Validation error during speech analysis: {e}")
            return SpeechAnalysisResponse(
                success=False,
                message=str(e)
            )
        except Exception as e:
            logger.exception("Unexpected error during speech analysis.")
            return SpeechAnalysisResponse(
                success=False,
                message="An internal error occurred during analysis."
            )
