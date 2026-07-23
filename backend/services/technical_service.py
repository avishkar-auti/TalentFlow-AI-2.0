"""Technical service — coding/technical assessment submission and result retrieval."""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

import firebase_admin.firestore


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TechnicalService:
    """Service for technical assessment submissions and evaluation results."""

    def _db(self):
        return firebase_admin.firestore.client()

    async def submit_technical(
        self, candidate_id: str, answers: Dict[str, Any], interview_id: str
    ) -> Dict[str, Any]:
        """Store a technical submission and queue evaluation."""
        submission_id = f"tech_{uuid.uuid4().hex[:8]}"
        record = {
            "id": submission_id,
            "candidate_id": candidate_id,
            "interview_id": interview_id,
            "answers": answers,
            "status": "submitted",
            "submitted_at": _now(),
        }
        (
            self._db()
            .collection("candidates")
            .document(candidate_id)
            .collection("technical_submissions")
            .document(submission_id)
            .set(record)
        )
        return {"status": "submitted", "submission_id": submission_id, "message": "Technical answers submitted — evaluation queued"}

    async def get_technical_result(self, candidate_id: str, interview_id: str) -> Dict[str, Any]:
        """Fetch technical evaluation result for a specific interview."""
        try:
            doc = (
                self._db()
                .collection("candidates")
                .document(candidate_id)
                .collection("technical_results")
                .document(interview_id)
                .get()
            )
            if not doc.exists:
                return {
                    "candidate_id": candidate_id,
                    "interview_id": interview_id,
                    "status": "not_evaluated",
                    "scores": {},
                }
            return doc.to_dict()
        except Exception:
            return {"candidate_id": candidate_id, "interview_id": interview_id, "status": "error"}
