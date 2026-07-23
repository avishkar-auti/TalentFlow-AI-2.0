"""Admin controller — system configuration, activity logs, and agent observability."""
from fastapi import APIRouter
from typing import Any, Dict, Optional

from backend.services.admin_service import AdminService
from backend.shared.response import success_response, APIResponse

router = APIRouter(tags=["Admin"])


@router.get("/admin/system-config", response_model=APIResponse)
async def get_system_config():
    svc = AdminService()
    config = await svc.get_system_config()
    return success_response(config)


@router.patch("/admin/system-config", response_model=APIResponse)
async def update_system_config(updates: Dict[str, Any]):
    svc = AdminService()
    config = await svc.update_system_config(updates)
    return success_response(config, "System config updated")


@router.get("/activity-logs", response_model=APIResponse)
async def list_activity_logs(
    limit: int = 100,
    agent: Optional[str] = None,
    start_time: Optional[str] = None,
):
    svc = AdminService()
    logs = await svc.list_activity_logs(limit=limit, agent=agent, start_time=start_time)
    return success_response(logs)


@router.get("/agent-runs", response_model=APIResponse)
async def list_agent_runs(
    limit: int = 100,
    agent: Optional[str] = None,
    success: Optional[bool] = None,
):
    svc = AdminService()
    runs = await svc.list_agent_runs(limit=limit, agent=agent, success=success)
    return success_response(runs)
