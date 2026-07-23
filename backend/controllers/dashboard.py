from fastapi import APIRouter
from backend.services.dashboard_service import DashboardService
from backend.shared.response import APIResponse

router = APIRouter()

@router.get("/stats", response_model=APIResponse)
async def get_stats():
    service = DashboardService()
    stats = await service.get_overall_stats()
    return APIResponse(success=True, data=stats)

@router.get("/pipeline", response_model=APIResponse)
async def get_pipeline_counts():
    service = DashboardService()
    counts = await service.get_pipeline_counts()
    return APIResponse(success=True, data=counts)

@router.get("/funnel", response_model=APIResponse)
async def get_funnel():
    service = DashboardService()
    funnel = await service.get_hiring_funnel()
    return APIResponse(success=True, data=funnel)

@router.get("/activity", response_model=APIResponse)
async def get_activity():
    service = DashboardService()
    activities = await service.get_recent_activity()
    return APIResponse(success=True, data=activities)
