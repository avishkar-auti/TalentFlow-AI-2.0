"""Admin service — system config management, activity logs, and agent-run observability."""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import firebase_admin.firestore


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AdminService:
    """Admin-only service for system configuration and audit trail queries."""

    def _db(self):
        return firebase_admin.firestore.client()

    async def get_system_config(self) -> Dict[str, Any]:
        """Read system config from Firestore 'system_config/main'."""
        doc = self._db().collection("system_config").document("main").get()
        if not doc.exists:
            return {
                "model_routing": {"default": "gemini-1.5-pro"},
                "feature_flags": {"proctoring_enabled": True, "email_notifications": True},
                "updated_at": _now(),
            }
        return doc.to_dict()

    async def update_system_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Merge updates into Firestore 'system_config/main'."""
        ref = self._db().collection("system_config").document("main")
        updates["updated_at"] = _now()
        ref.set(updates, merge=True)
        doc = ref.get()
        return doc.to_dict()

    async def list_activity_logs(
        self,
        limit: int = 100,
        agent: Optional[str] = None,
        start_time: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return filterable audit trail from 'activity_logs' collection."""
        ref = self._db().collection("activity_logs").order_by(
            "created_at", direction=firebase_admin.firestore.Query.DESCENDING
        ).limit(limit)
        docs = ref.stream()
        results = [doc.to_dict() for doc in docs]
        if agent:
            results = [r for r in results if r.get("agent_name") == agent]
        if start_time:
            results = [r for r in results if r.get("created_at", "") >= start_time]
        return results

    async def list_agent_runs(
        self,
        limit: int = 100,
        agent: Optional[str] = None,
        success: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Return tool-call level logs from 'agent_runs' collection."""
        ref = self._db().collection("agent_runs").order_by(
            "created_at", direction=firebase_admin.firestore.Query.DESCENDING
        ).limit(limit)
        docs = ref.stream()
        results = [doc.to_dict() for doc in docs]
        if agent:
            results = [r for r in results if r.get("agent") == agent]
        if success is not None:
            results = [r for r in results if r.get("success") == success]
        return results
