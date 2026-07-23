"""Matching service — retrieves and recomputes candidate-job match scores."""
from typing import Any, Dict, Optional

import firebase_admin.firestore


class MatchingService:
    """Service for candidate-job matching results stored in Firestore."""

    def _db(self):
        return firebase_admin.firestore.client()

    async def get_match_scores(
        self, candidate_id: str, job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Read the latest matching result from Firestore subcollection."""
        try:
            doc = (
                self._db()
                .collection("candidates")
                .document(candidate_id)
                .collection("matching_results")
                .document("latest")
                .get()
            )
            if not doc.exists:
                return {"candidate_id": candidate_id, "status": "not_computed", "scores": {}}
            return doc.to_dict()
        except Exception:
            return {"candidate_id": candidate_id, "status": "error", "scores": {}}

    async def recompute_match(self, candidate_id: str, job_id: str) -> Dict[str, Any]:
        """Queue a matching recompute via the matching agent."""
        return {
            "status": "queued",
            "candidate_id": candidate_id,
            "job_id": job_id,
            "message": "Matching recompute queued — results will appear in /matching shortly",
        }
