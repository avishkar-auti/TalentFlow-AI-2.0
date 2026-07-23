"""Notification service — manages recruiter notifications and candidate email triggers."""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import firebase_admin.firestore


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class NotificationService:
    """Read/write notifications in Firestore 'notifications' collection."""

    def _db(self):
        return firebase_admin.firestore.client()

    async def list_notifications(
        self, unread_only: bool = False, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Return recruiter notification feed, optionally filtering to unread only."""
        ref = self._db().collection("notifications").order_by(
            "sent_at", direction=firebase_admin.firestore.Query.DESCENDING
        ).limit(limit)
        docs = ref.stream()
        results = [doc.to_dict() for doc in docs]
        if unread_only:
            results = [n for n in results if not n.get("read", False)]
        return results

    async def send_notification(
        self,
        candidate_id: str,
        subject: str,
        body: str,
        channel: str = "email",
    ) -> Dict[str, Any]:
        """Create a notification record and (optionally) trigger email delivery."""
        notif_id = f"notif_{uuid.uuid4().hex[:10]}"
        record = {
            "id": notif_id,
            "candidate_id": candidate_id,
            "subject": subject,
            "body": body,
            "channel": channel,
            "sent_at": _now(),
            "read": False,
        }
        self._db().collection("notifications").document(notif_id).set(record)
        return record

    async def mark_read(self, notification_id: str) -> Dict[str, Any]:
        """Mark a notification as read."""
        ref = self._db().collection("notifications").document(notification_id)
        ref.update({"read": True, "read_at": _now()})
        doc = ref.get()
        return doc.to_dict() if doc.exists else {"id": notification_id, "read": True}
