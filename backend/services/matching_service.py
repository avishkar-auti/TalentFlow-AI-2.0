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
        """Compute matching score via MatchingAgent and persist to Firestore.

        Only writes a score when the agent actually produced one — never fabricates
        a fallback number, since that would overwrite a real prior score with a fake
        static one and mislead recruiters into thinking every candidate scored the same.
        """
        try:
            from agents.matching_agent.agent import MatchingAgent
            agent = MatchingAgent()
            result = await agent.process(candidate_id, job_id)

            score = result.get("overallMatch")
            if score is not None:
                self._db().collection("candidates").document(candidate_id).set({
                    "overallMatch": score,
                    "overallScore": score,
                    "atsScore": score,
                }, merge=True)

            return {
                "status": "completed" if score is not None else "no_score_returned",
                "candidate_id": candidate_id,
                "job_id": job_id,
                "result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "candidate_id": candidate_id,
                "job_id": job_id,
                "error": str(e)
            }

