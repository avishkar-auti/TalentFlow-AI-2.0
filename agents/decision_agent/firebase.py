"""
Firebase Data Access Layer for Decision Agent.
Reads subcollection outputs from Resume, Matching, Background, Technical, Speech agents, and writes final Decision report.
"""
import logging
from typing import Dict, Any, Optional
from backend.firebase import firestore

logger = logging.getLogger("firebase")

async def fetch_all_candidate_agent_data(candidate_id: str) -> Dict[str, Any]:
    """Fetches all agent subcollection documents for a candidate from Firestore."""
    data = {}
    try:
        data["resume"] = await firestore.get_document(f"candidates/{candidate_id}/resume_analysis", "latest") or {}
        data["matching"] = await firestore.get_document(f"candidates/{candidate_id}/matching", "latest") or {}
        data["background"] = await firestore.get_document(f"candidates/{candidate_id}/background", "latest") or {}
        data["technical"] = await firestore.get_document(f"candidates/{candidate_id}/technical", "latest") or {}
        data["speech"] = await firestore.get_document(f"candidates/{candidate_id}/speech", "latest") or {}
        data["candidate"] = await firestore.get_document("candidates", candidate_id) or {}
    except Exception as e:
        logger.warning(f"Failed to fetch complete subcollection data for candidate {candidate_id}: {e}")

    return data

async def save_decision_result(candidate_id: str, decision_data: Dict[str, Any]) -> None:
    """Saves decision report to Firestore."""
    try:
        await firestore.set_document(
            collection=f"candidates/{candidate_id}/decision",
            document_id="latest",
            data=decision_data,
            merge=True
        )
        # Update candidate summary
        await firestore.set_document("candidates", candidate_id, {
            "overallScore": decision_data.get("overallScore"),
            "recommendation": decision_data.get("recommendation"),
            "decisionComplete": True,
            "pipelineStage": "decision"
        }, merge=True)
        logger.info(f"Saved decision report for candidate {candidate_id} to Firestore.")
    except Exception as e:
        logger.error(f"Failed to save decision result for candidate {candidate_id}: {e}")
