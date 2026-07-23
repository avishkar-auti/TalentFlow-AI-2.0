"""Firestore repository for Technical Agent."""
import logging
from typing import Dict, Any, Optional

try:
    from backend.tools.firebase import db
except ImportError:
    logging.warning("backend.tools.firebase not found. Using mock db object.")
    db = None

logger = logging.getLogger(__name__)

class TechnicalRepository:
    """Repository for accessing Firestore data related to technical evaluation."""
    
    def __init__(self):
        self.collection_name = "candidates"
        
    def get_interview_data(self, candidate_id: str, interview_id: str) -> Optional[Dict[str, Any]]:
        """Fetch transcript and code submissions."""
        if db is None:
            logger.error("Database connection not initialized.")
            return None
            
        try:
            doc_ref = db.collection(self.collection_name).document(candidate_id).collection("interviews").document(interview_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error fetching interview data: {e}")
            return None
            
    def save_technical_evaluation(self, candidate_id: str, interview_id: str, result_data: Dict[str, Any]) -> bool:
        """Save the technical evaluation result to Firestore."""
        if db is None:
            logger.error("Database connection not initialized.")
            return False
            
        try:
            doc_ref = db.collection(self.collection_name).document(candidate_id).collection("technical").document(interview_id)
            doc_ref.set(result_data)
            logger.info(f"Successfully saved technical evaluation for candidate {candidate_id}, interview {interview_id}.")
            return True
        except Exception as e:
            logger.error(f"Error saving technical evaluation: {e}")
            return False
