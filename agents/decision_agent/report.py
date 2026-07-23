"""
PDF Hiring Report & Plain-Language Business Remarks Generator.
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def generate_business_summary(
    candidate_name: str,
    job_title: str,
    overall_score: float,
    recommendation: str,
    scores: Dict[str, float]
) -> Dict[str, Any]:
    """Generates plain business language summary without revealing agent plumbing."""
    
    strengths = []
    concerns = []

    if scores.get("technicalScore", 0) >= 80:
        strengths.append("Demonstrated solid technical proficiency and problem-solving skills.")
    elif scores.get("technicalScore", 0) < 65:
        concerns.append("Technical assessment score indicates room for growth in core tech stack.")

    if scores.get("atsScore", 0) >= 80:
        strengths.append("High alignment with role keyword requirements and qualifications.")

    if scores.get("speechScore", 0) >= 80:
        strengths.append("Strong communication clarity, vocabulary fluency, and structured answers.")

    if not strengths:
        strengths.append("Solid overall professional background and relevant domain experience.")

    if not concerns:
        concerns.append("No major red flags or critical skill deficiencies observed.")

    remarks = (
        f"{candidate_name} achieved an overall match score of {overall_score}% for the {job_title} position. "
        f"Based on full assessment evaluation, the candidate is recommended as a {recommendation.replace('_', ' ')}."
    )

    return {
        "summary": remarks,
        "strengths": strengths,
        "concerns": concerns,
        "recommendation": recommendation
    }
