"""Dashboard schemas."""
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class PipelineCount(BaseModel):
    stage: str
    count: int

class FunnelData(BaseModel):
    stage: str
    conversion_rate: float

class ActivityFeedItem(BaseModel):
    id: str
    action: str
    description: str
    timestamp: datetime
    user_id: str

class DashboardStats(BaseModel):
    total_candidates: int
    active_jobs: int
    interviews_scheduled: int
    recent_activities: List[ActivityFeedItem]
    pipeline_counts: List[PipelineCount]
    funnel: List[FunnelData]
