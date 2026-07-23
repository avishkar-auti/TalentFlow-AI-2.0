from fastapi import APIRouter, HTTPException, Path
from .service import background_service
from .schemas import BackgroundCheckResponse
from .firebase import firebase_client

router = APIRouter(
    prefix="/api/v1/candidates",
    tags=["Background Check"]
)

@router.post("/{candidate_id}/background", response_model=BackgroundCheckResponse)
async def trigger_background_check(
    candidate_id: str = Path(..., description="The ID of the candidate"),
    job_id: str = "default_job_id" # Real app would likely pass in body or query
):
    """
    Trigger a background check for the candidate.
    """
    try:
        result = await background_service.run_background_check(candidate_id, job_id)
        return BackgroundCheckResponse(
            candidate_id=candidate_id,
            job_id=job_id,
            result=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{candidate_id}/background", response_model=BackgroundCheckResponse)
async def get_background_check(
    candidate_id: str = Path(..., description="The ID of the candidate"),
    job_id: str = "default_job_id"
):
    """
    Get the results of a background check.
    """
    try:
        # Check cache or DB first
        cached = await firebase_client.get_cached_background_check(candidate_id, job_id)
        if cached:
             return BackgroundCheckResponse(
                candidate_id=candidate_id,
                job_id=job_id,
                result=cached
            )
        else:
             raise HTTPException(status_code=404, detail="Background check not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
