"""
Matching Controller API Endpoints.
"""
from fastapi import APIRouter, HTTPException
from agents.matching_agent.agent import MatchingAgent
from backend.shared.response import success_response

router = APIRouter(prefix="/matching", tags=["Matching Agent"])

@router.post("/evaluate/{candidate_id}")
async def evaluate_matching(candidate_id: str, job_id: str = "j1"):
    try:
        agent = MatchingAgent()
        res = await agent.process(candidate_id, job_id)
        return success_response(data=res, message="Role fit matching evaluation complete.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
