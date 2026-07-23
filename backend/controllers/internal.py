"""Internal orchestrator endpoints — pipeline advancement and state inspection (admin/debug)."""
from fastapi import APIRouter

from backend.services.orchestrator_service import OrchestratorService
from backend.shared.response import success_response, APIResponse

router = APIRouter(tags=["Internal"])


@router.post("/internal/orchestrator/advance/{candidate_id}", response_model=APIResponse)
async def advance_pipeline(candidate_id: str):
    svc = OrchestratorService()
    result = await svc.advance_pipeline(candidate_id)
    return success_response(result, "Pipeline advance triggered")


@router.get("/internal/orchestrator/state/{candidate_id}", response_model=APIResponse)
async def get_pipeline_state(candidate_id: str):
    svc = OrchestratorService()
    state = await svc.get_pipeline_state(candidate_id)
    return success_response(state)
