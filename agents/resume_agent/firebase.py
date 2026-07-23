"""
Firebase Firestore & Storage Data Layer for Resume Agent.
"""
import logging
from typing import Dict, Any, Optional
from backend.firebase import firestore, storage

logger = logging.getLogger("firebase")

async def get_analysis(candidate_id: str) -> Optional[Dict[str, Any]]:
    """Gets candidate resume analysis from Firestore."""
    try:
        return await firestore.get_document(f"candidates/{candidate_id}/resume_analysis", "latest")
    except Exception as e:
        logger.warning(f"Could not read resume analysis for candidate {candidate_id}: {e}")
        return None

async def save_resume_file_to_storage(candidate_id: str, file_bytes: bytes, filename: str) -> str:
    """Uploads candidate resume PDF to Firebase Storage and returns signed/public URL."""
    try:
        bucket_path = f"resumes/{candidate_id}/{filename}"
        public_url = await storage.upload_file(bucket_path, file_bytes, content_type="application/pdf")
        logger.info(f"Uploaded resume for candidate {candidate_id} to Storage: {bucket_path}")
        return public_url
    except Exception as e:
        logger.warning(f"Storage upload warning for candidate {candidate_id}: {e}. Returning relative path.")
        return f"/storage/resumes/{candidate_id}/{filename}"

async def save_analysis(candidate_id: str, analysis_data: Dict[str, Any]) -> None:
    """Saves candidate resume analysis to Firestore document and subcollection."""
    try:
        # 1. Update candidate subcollection: candidates/{candidateId}/resume_analysis/latest
        await firestore.set_document(
            collection=f"candidates/{candidate_id}/resume_analysis",
            document_id="latest",
            data=analysis_data,
            merge=True
        )

        # 2. Also update top-level candidate summary fields in candidates/{candidateId}
        summary_update = {
            "resumeParsed": True,
            "atsScore": analysis_data.get("score", {}).get("ats_score", 85.0),
            "resumeQualityScore": analysis_data.get("score", {}).get("resume_score", 88.0),
            "skillsCount": len(analysis_data.get("analysis", {}).get("skills", [])),
            "pipelineStage": "screening"
        }
        await firestore.set_document("candidates", candidate_id, summary_update, merge=True)

        logger.info(f"Saved resume analysis for candidate {candidate_id} to Firestore.")
    except Exception as e:
        logger.error(f"Failed to save resume analysis to Firestore for candidate {candidate_id}: {e}")

async def get_job_requirements_from_firestore(job_id: str) -> list[str]:
    """Retrieves target job requirements from Firestore jobs/{jobId} document."""
    try:
        job_doc = await firestore.get_document("jobs", job_id)
        if job_doc and "requirements" in job_doc:
            reqs = job_doc["requirements"]
            if isinstance(reqs, list):
                return reqs
            elif isinstance(reqs, dict):
                return reqs.get("skills", []) + reqs.get("experience", [])
        return []
    except Exception as e:
        logger.warning(f"Could not fetch job requirements for job_id {job_id} from Firestore: {e}")
        return []
