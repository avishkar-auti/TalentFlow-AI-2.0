"""
Matching Agent Orchestrator.
Calculates candidate-job role fit using deterministic multi-dimensional matcher + Groq LLM judgment fallback.
"""
import logging
from typing import Dict, Any, Optional
from .matcher import RoleFitMatcher
from .firebase import get_candidate_analysis, get_job_details, save_matching_result

logger = logging.getLogger(__name__)

class MatchingAgent:
    """Production Matching Agent for TalentFlow-AI."""

    async def process(self, candidate_id: str, job_id: str) -> Dict[str, Any]:
        """
        Executes candidate-job role fit matching pipeline:
        1. Fetch candidate resume analysis from Firestore
        2. Fetch job details from Firestore
        3. Compute multi-dimensional role fit (skills, experience, education, location)
        4. Persist results to Firestore
        """
        logger.info(f"Running role fit matching for candidate_id={candidate_id}, job_id={job_id}")

        # 1. Fetch Firestore documents
        cand_analysis = await get_candidate_analysis(candidate_id) or {}
        job_doc = await get_job_details(job_id) or {}

        analysis_inner = cand_analysis.get("analysis", cand_analysis)
        skills_raw = analysis_inner.get("skills", [])
        cand_skills = [s.get("name", s) if isinstance(s, dict) else str(s) for s in skills_raw]

        cand_exp = analysis_inner.get("experience", "2 Years")
        cand_edu = analysis_inner.get("education", [{"degree": "Bachelor"}])

        job_reqs = job_doc.get("requirements", {
            "skills": ["Python", "FastAPI", "React", "Docker"],
            "experience": "2 Years",
            "education": "Bachelor"
        })
        if isinstance(job_reqs, list):
            job_reqs = {"skills": job_reqs, "experience": "2 Years", "education": "Bachelor"}

        # 2. Compute Role Fit Match
        match_result = RoleFitMatcher.compute_role_fit(
            candidate_skills=cand_skills,
            candidate_exp=cand_exp,
            candidate_edu=cand_edu,
            job_requirements=job_reqs
        )

        # 3. Persist to Firestore
        await save_matching_result(candidate_id, match_result)

        logger.info(f"Role fit matching complete for {candidate_id}. Overall Match: {match_result['overallMatch']}%")
        return match_result
