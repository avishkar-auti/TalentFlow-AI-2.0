"""Proctoring service — persists and retrieves interview proctoring flags from Firestore."""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

import firebase_admin.firestore

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProctoringService:
    """Stores and retrieves proctoring flags for interview sessions."""

    def _db(self):
        return firebase_admin.firestore.client()

    async def store_flags(self, interview_id: str, flags: List[Dict[str, Any]]) -> None:
        """Batch-append emitted flags to Firestore subcollection."""
        if not flags:
            return
        try:
            db = self._db()
            batch = db.batch()
            col_ref = (
                db.collection("interviews")
                .document(interview_id)
                .collection("proctoring_flags")
            )
            for flag in flags:
                doc_ref = col_ref.document()
                batch.set(doc_ref, {**flag, "stored_at": _now()})
            batch.commit()
            logger.info(f"Stored {len(flags)} proctoring flags for interview {interview_id}")
        except Exception as exc:
            logger.error(f"Failed to store proctoring flags for {interview_id}: {exc}")

    async def get_proctoring_summary(self, interview_id: str) -> Dict[str, Any]:
        """Retrieve and aggregate all stored proctoring flags for a session."""
        try:
            docs = (
                self._db()
                .collection("interviews")
                .document(interview_id)
                .collection("proctoring_flags")
                .order_by("timestamp")
                .stream()
            )
            flags = [doc.to_dict() for doc in docs]
            formatted = [
                {
                    "event": f.get("event", "unknown"),
                    "start": f.get("start_timestamp", f.get("timestamp", "")[:19]),
                    "duration_s": f.get("duration_seconds", 0),
                    "duration_seconds": f.get("duration_seconds", 0),
                    "warning_number": f.get("warning_number", 0),
                    "user_message": f.get("user_message", ""),
                    "is_terminated": f.get("is_terminated", False),
                    "details": f.get("details", {}),
                    "timestamp": f.get("timestamp", ""),
                }
                for f in flags
            ]
            return {
                "interview_id": interview_id,
                "total_flags": len(flags),
                "summary": f"{len(flags)} warning flag(s) recorded",
                "flags": formatted,
            }
        except Exception as exc:
            logger.error(f"Failed to fetch proctoring summary for {interview_id}: {exc}")
            return {
                "interview_id": interview_id,
                "total_flags": 0,
                "summary": "unavailable",
                "flags": [],
            }

    async def clear_flags(self, interview_id: str) -> None:
        """Delete all stored proctoring flags for a session (for testing/reset)."""
        try:
            col_ref = (
                self._db()
                .collection("interviews")
                .document(interview_id)
                .collection("proctoring_flags")
            )
            for doc in col_ref.stream():
                doc.reference.delete()
        except Exception as exc:
            logger.error(f"Failed to clear proctoring flags for {interview_id}: {exc}")
