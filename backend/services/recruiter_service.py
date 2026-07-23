"""Recruiter service — manages recruiter accounts in Firestore."""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

import firebase_admin.firestore


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RecruiterService:
    """CRUD service for recruiter records in 'recruiters' Firestore collection."""

    def _db(self):
        return firebase_admin.firestore.client()

    async def list_recruiters(self) -> List[Dict[str, Any]]:
        docs = self._db().collection("recruiters").stream()
        return [doc.to_dict() for doc in docs]

    async def create_recruiter(
        self, name: str, email: str, role: str = "recruiter"
    ) -> Dict[str, Any]:
        rec_id = f"rec_{uuid.uuid4().hex[:8]}"
        record = {
            "id": rec_id,
            "name": name,
            "email": email,
            "role": role,
            "created_at": _now(),
            "updated_at": _now(),
        }
        self._db().collection("recruiters").document(rec_id).set(record)
        return record

    async def update_role(self, recruiter_id: str, role: str) -> Dict[str, Any]:
        ref = self._db().collection("recruiters").document(recruiter_id)
        ref.update({"role": role, "updated_at": _now()})
        doc = ref.get()
        return doc.to_dict() if doc.exists else {"id": recruiter_id, "role": role}
