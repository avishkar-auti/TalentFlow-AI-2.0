"""
Firebase Firestore Data Persistence for Matching Agent.
"""
import logging
from typing import Dict, Any, Optional
from backend.firebase import firestore

logger = logging.getLogger("firebase")

async def get_candidate_analysis(candidate_id: str) -> Optional[Dict[str, Any]]:
    """Gets candidate resume analysis from Firestore."""
    try:
        return await firestore.get_document(f"candidates/{candidate_id}/resume_analysis", "latest")
    except Exception as e:
        logger.warning(f"Could not read resume analysis for candidate {candidate_id}: {e}")
        return None

async def get_job_details(job_id: str) -> Optional[Dict[str, Any]]:
    """Gets job requirements from Firestore."""
    try:
        return await firestore.get_document("jobs", job_id)
    except Exception as e:
        logger.warning(f"Could not read job details for job {job_id}: {e}")
        return None

async def save_matching_result(candidate_id: str, matching_data: Dict[str, Any]) -> None:
    """Saves role fit matching result to Firestore."""
    try:
        await firestore.set_document(
            collection=f"candidates/{candidate_id}/matching",
            document_id="latest",
            data=matching_data,
            merge=True
        )
        # Update top-level candidate match score
        await firestore.set_document("candidates", candidate_id, {
            "overallMatch": matching_data.get("overallMatch", 85.0),
            "matchingComplete": True
        }, merge=True)
        logger.info(f"Saved matching result for candidate {candidate_id} to Firestore.")
    except Exception as e:
        logger.error(f"Failed to save matching result for candidate {candidate_id}: {e}")
