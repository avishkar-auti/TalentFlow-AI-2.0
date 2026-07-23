"""Firestore repository for Speech Agent."""
import logging
from typing import Dict, Any, Optional
# Assuming there's a shared tools module. We'll use a mocked internal interface or typical firebase admin structure.
# Since we must interact with the shared tools/ layer, we'll import from backend.tools.firebase (assuming it exists)
try:
    from backend.tools.firebase import db
except ImportError:
    logging.warning("backend.tools.firebase not found. Using mock db object.")
    db = None

logger = logging.getLogger(__name__)

class SpeechRepository:
    """Repository for accessing Firestore data related to speech analysis."""
    
    def __init__(self):
        self.collection_name = "candidates"
        
    def get_interview_transcript(self, candidate_id: str, interview_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the interview data including transcript from Firestore.
        
        Args:
            candidate_id: The candidate ID.
            interview_id: The interview ID.
            
        Returns:
            Dictionary containing interview data or None if not found.
        """
        if db is None:
            logger.error("Database connection not initialized.")
            return None
            
        try:
            doc_ref = db.collection(self.collection_name).document(candidate_id).collection("interviews").document(interview_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            logger.warning(f"Interview {interview_id} for candidate {candidate_id} not found.")
            return None
        except Exception as e:
            logger.error(f"Error fetching interview transcript: {e}")
            return None
            
    def save_speech_analysis(self, candidate_id: str, interview_id: str, result_data: Dict[str, Any]) -> bool:
        """
        Save the speech analysis result to Firestore.
        
        Args:
            candidate_id: The candidate ID.
            interview_id: The interview ID.
            result_data: The analysis data to save.
            
        Returns:
            True if successful, False otherwise.
        """
        if db is None:
            logger.error("Database connection not initialized.")
            return False
            
        try:
            doc_ref = db.collection(self.collection_name).document(candidate_id).collection("speech").document(interview_id)
            doc_ref.set(result_data)
            logger.info(f"Successfully saved speech analysis for candidate {candidate_id}, interview {interview_id}.")
            return True
        except Exception as e:
            logger.error(f"Error saving speech analysis: {e}")
            return False
