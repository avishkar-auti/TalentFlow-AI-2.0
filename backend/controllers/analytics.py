"""Analytics controller — hiring funnel, stage counts, and activity feed."""
from fastapi import APIRouter

from backend.services.analytics_service import AnalyticsService
from backend.shared.response import success_response, APIResponse

router = APIRouter(tags=["Analytics"])


@router.get("/analytics/funnel", response_model=APIResponse)
async def get_funnel():
    svc = AnalyticsService()
    data = await svc.get_funnel_data()
    return success_response(data)


@router.get("/analytics/stage-counts", response_model=APIResponse)
async def get_stage_counts():
    svc = AnalyticsService()
    counts = await svc.get_stage_counts()
    return success_response(counts)


@router.get("/analytics/activity-feed", response_model=APIResponse)
async def get_activity_feed(limit: int = 20):
    svc = AnalyticsService()
    feed = await svc.get_activity_feed(limit=limit)
    return success_response(feed)
