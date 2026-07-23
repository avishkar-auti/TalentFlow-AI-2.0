"""Speech service — fluency and confidence analysis retrieval from Firestore."""
from typing import Any, Dict

import firebase_admin.firestore


class SpeechService:
    """Service for speech agent analysis results (fluency, confidence, pace)."""

    def _db(self):
        return firebase_admin.firestore.client()

    async def get_speech_analysis(self, candidate_id: str, interview_id: str) -> Dict[str, Any]:
        """Fetch speech analysis result for a specific interview session."""
        try:
            doc = (
                self._db()
                .collection("candidates")
                .document(candidate_id)
                .collection("speech_analysis")
                .document(interview_id)
                .get()
            )
            if not doc.exists:
                return {
                    "candidate_id": candidate_id,
                    "interview_id": interview_id,
                    "status": "not_analyzed",
                    "metrics": {},
                }
            return doc.to_dict()
        except Exception:
            return {"candidate_id": candidate_id, "interview_id": interview_id, "status": "error"}
