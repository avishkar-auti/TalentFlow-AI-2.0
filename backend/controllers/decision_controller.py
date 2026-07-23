"""
Decision Controller API Endpoints.
"""
from fastapi import APIRouter, HTTPException
from agents.decision_agent.agent import DecisionAgent
from backend.shared.response import success_response

router = APIRouter(prefix="/decision", tags=["Decision Agent"])

@router.post("/generate/{candidate_id}")
async def generate_decision(candidate_id: str, job_id: str = "j1"):
    try:
        agent = DecisionAgent()
        res = await agent.process(candidate_id, job_id)
        return success_response(data=res, message="Hiring decision report generated successfully.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
