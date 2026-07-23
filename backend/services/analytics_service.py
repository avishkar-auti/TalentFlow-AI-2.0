"""Analytics service — hiring funnel, stage counts, and activity feed aggregations."""
from typing import Any, Dict, List

import firebase_admin.firestore

PIPELINE_STAGES = [
    "applied", "screening", "interview", "technical", "decision", "offer", "rejected"
]

STAGE_LABELS = {
    "applied": "Applied",
    "screening": "Screening",
    "interview": "Interview",
    "technical": "Technical",
    "decision": "Decision",
    "offer": "Offer",
    "rejected": "Rejected",
}


class AnalyticsService:
    """Aggregation service for dashboard analytics and hiring funnel data."""

    def _db(self):
        return firebase_admin.firestore.client()

    async def get_stage_counts(self) -> Dict[str, int]:
        """Return candidate counts per Kanban pipeline stage."""
        candidates = self._db().collection("candidates").stream()
        counts: Dict[str, int] = {label: 0 for label in STAGE_LABELS.values()}
        for doc in candidates:
            data = doc.to_dict()
            stage = data.get("pipeline_stage", "applied").lower()
            label = STAGE_LABELS.get(stage, "Applied")
            counts[label] = counts.get(label, 0) + 1
        return counts

    async def get_funnel_data(self) -> Dict[str, Any]:
        """Return hiring funnel chart data with per-stage conversion percentages."""
        counts = await self.get_stage_counts()
        total = counts.get("Applied", 0)
        stages = []
        prev = total or 1
        for stage in PIPELINE_STAGES:
            label = STAGE_LABELS[stage]
            count = counts.get(label, 0)
            pct = round((count / prev) * 100, 1) if prev > 0 else 0.0
            stages.append({"stage": label, "count": count, "pct_of_prev": pct})
            prev = count if count > 0 else prev
        return {"total_candidates": total, "stages": stages}

    async def get_activity_feed(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Return recent activity items from the activity_logs collection."""
        docs = (
            self._db()
            .collection("activity_logs")
            .order_by("created_at", direction=firebase_admin.firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        return [doc.to_dict() for doc in docs]
