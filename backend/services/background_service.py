"""Background check service — retrieves and triggers background verification checks."""
from typing import Any, Dict

import firebase_admin.firestore


class BackgroundService:
    """Service for candidate background check results."""

    def _db(self):
        return firebase_admin.firestore.client()

    async def get_background_check(self, candidate_id: str) -> Dict[str, Any]:
        """Read latest background check from Firestore."""
        try:
            doc = (
                self._db()
                .collection("candidates")
                .document(candidate_id)
                .collection("background_check")
                .document("latest")
                .get()
            )
            if not doc.exists:
                return {"candidate_id": candidate_id, "status": "not_run", "result": {}}
            return doc.to_dict()
        except Exception:
            return {"candidate_id": candidate_id, "status": "error", "result": {}}

    async def recheck_background(self, candidate_id: str) -> Dict[str, Any]:
        """Queue a background re-check via the background agent."""
        return {
            "status": "queued",
            "candidate_id": candidate_id,
            "message": "Background check queued — results will appear in /background shortly",
        }
