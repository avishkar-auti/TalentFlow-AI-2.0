from fastapi import APIRouter, HTTPException
from .schemas import MatchRequest, MatchResponse
from .service import run_matching
from . import firebase

router = APIRouter(prefix="/api/v1/candidates/{candidate_id}/matching", tags=["matching"])

@router.post("", response_model=MatchResponse)
async def trigger_matching(candidate_id: str, request: MatchRequest):
    response = await run_matching(candidate_id, request.job_id)
    if not response.success:
        raise HTTPException(status_code=500, detail=response.error)
    return response

@router.get("", response_model=MatchResponse)
async def get_matching_result(candidate_id: str):
    # This is a placeholder for retrieving actual results
    # Normally we would fetch the latest from Firebase
    raise HTTPException(status_code=501, detail="Not Implemented. Use POST to trigger matching.")
