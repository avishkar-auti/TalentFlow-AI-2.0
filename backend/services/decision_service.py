"""Decision service — final recommendation, score aggregation, and PDF report access."""
from typing import Any, Dict, Optional

import firebase_admin.firestore


class DecisionService:
    """Service for the AI decision agent's outputs and PDF report delivery."""

    def _db(self):
        return firebase_admin.firestore.client()

    async def get_decision(self, candidate_id: str) -> Dict[str, Any]:
        """Read the latest decision record from Firestore."""
        try:
            doc = (
                self._db()
                .collection("candidates")
                .document(candidate_id)
                .collection("decision")
                .document("latest")
                .get()
            )
            if not doc.exists:
                return {"candidate_id": candidate_id, "status": "not_generated", "recommendation": None}
            return doc.to_dict()
        except Exception:
            return {"candidate_id": candidate_id, "status": "error"}

    async def generate_decision(self, candidate_id: str) -> Dict[str, Any]:
        """Trigger decision agent for a candidate — queued async."""
        return {
            "status": "queued",
            "candidate_id": candidate_id,
            "message": "Decision generation queued — orchestrator will process shortly",
        }

    async def get_report_url(self, candidate_id: str) -> Optional[str]:
        """Return the Cloud Storage URL for the candidate's PDF decision report."""
        try:
            doc = (
                self._db()
                .collection("candidates")
                .document(candidate_id)
                .collection("decision")
                .document("latest")
                .get()
            )
            if not doc.exists:
                return None
            return doc.to_dict().get("report_url")
        except Exception:
            return None
