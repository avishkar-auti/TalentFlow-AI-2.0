"""
Multi-dimensional Role Fit Matcher Engine.
"""
import logging
from typing import Dict, Any, List
from .skills import evaluate_skill_match
from .experience import evaluate_experience_match
from .education import evaluate_education_match

logger = logging.getLogger(__name__)

class RoleFitMatcher:
    """Computes overall job-candidate role fit match score."""

    @staticmethod
    def compute_role_fit(
        candidate_skills: List[str],
        candidate_exp: Any,
        candidate_edu: Any,
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        req_skills = job_requirements.get("skills", [])
        req_exp = job_requirements.get("experience", "2 Years")
        req_edu = job_requirements.get("education", "Bachelor")

        skill_score, matched_skills, missing_skills = evaluate_skill_match(candidate_skills, req_skills)
        exp_score = evaluate_experience_match(candidate_exp, req_exp)
        edu_score = evaluate_education_match(candidate_edu, req_edu)
        location_score = 100.0  # Default full match for remote/flexible

        overall = round(
            (skill_score * 0.40) +
            (exp_score * 0.25) +
            (edu_score * 0.20) +
            (location_score * 0.15),
            1
        )

        return {
            "skillMatch": float(skill_score),
            "experienceMatch": float(exp_score),
            "educationMatch": float(edu_score),
            "locationMatch": float(location_score),
            "overallMatch": float(overall),
            "missingSkills": missing_skills,
            "matchedSkills": matched_skills,
            "confidence": 0.95
        }
