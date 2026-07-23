"""Async Firestore bridge — persists proctoring flags during live WebSocket sessions."""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProctoringStore:
    """Lightweight async Firestore bridge used inside WebSocket sessions.

    Separate from backend.services.proctoring_service to keep the agent layer
    independent of the FastAPI service layer.
    """

    def __init__(self, interview_id: str):
        self.interview_id = interview_id
        self._db = None

    def _get_db(self):
        if self._db is None:
            import firebase_admin.firestore
            self._db = firebase_admin.firestore.client()
        return self._db

    async def store_flags(self, flags: List[Dict[str, Any]]) -> None:
        """Batch-write emitted flags to Firestore proctoring_flags subcollection."""
        if not flags:
            return
        try:
            db = self._get_db()
            batch = db.batch()
            col_ref = (
                db.collection("interviews")
                .document(self.interview_id)
                .collection("proctoring_flags")
            )
            for flag in flags:
                doc_ref = col_ref.document()
                batch.set(doc_ref, {**flag, "stored_at": _now()})
            batch.commit()
            logger.info(
                f"Stored {len(flags)} proctoring flag(s) for interview {self.interview_id}"
            )
        except Exception as exc:
            logger.error(f"Failed to store proctoring flags for {self.interview_id}: {exc}")

    async def get_summary(self) -> Dict[str, Any]:
        """Retrieve and aggregate all stored flags for this session."""
        try:
            db = self._get_db()
            docs = (
                db.collection("interviews")
                .document(self.interview_id)
                .collection("proctoring_flags")
                .order_by("timestamp")
                .stream()
            )
            flags = [doc.to_dict() for doc in docs]
            return {
                "interview_id": self.interview_id,
                "total_flags": len(flags),
                "summary": f"{len(flags)} flag(s) detected",
                "flags": flags,
            }
        except Exception as exc:
            logger.error(f"Failed to fetch proctoring summary for {self.interview_id}: {exc}")
            return {
                "interview_id": self.interview_id,
                "total_flags": 0,
                "summary": "unavailable",
                "flags": [],
            }
