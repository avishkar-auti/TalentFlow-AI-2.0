"""Application service — manages candidate ↔ job application records in Firestore."""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import firebase_admin.firestore


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ApplicationService:
    """CRUD service for job applications in the 'applications' Firestore collection."""

    def _db(self):
        return firebase_admin.firestore.client()

    async def create_application(
        self,
        candidate_id: str,
        job_id: str,
        cover_note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new application record linking a candidate to a job."""
        app_id = f"app_{uuid.uuid4().hex[:10]}"
        record = {
            "id": app_id,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "cover_note": cover_note or "",
            "status": "applied",
            "created_at": _now(),
            "updated_at": _now(),
        }
        self._db().collection("applications").document(app_id).set(record)
        return record

    async def get_application(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single application by ID."""
        doc = self._db().collection("applications").document(application_id).get()
        if not doc.exists:
            return None
        return doc.to_dict()

    async def list_applications(
        self,
        candidate_id: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List applications with optional candidate or job filters."""
        ref = self._db().collection("applications")
        if candidate_id:
            ref = ref.where("candidate_id", "==", candidate_id)
        if job_id:
            ref = ref.where("job_id", "==", job_id)
        return [doc.to_dict() for doc in ref.stream()]
