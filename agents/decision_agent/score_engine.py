"""
Decision Score Engine.
Aggregates all multi-agent pipeline scores using deterministic formula.
"""
from typing import Dict, Any

def calculate_overall_score(
    resume_score: float,
    ats_score: float,
    matching_score: float,
    background_score: float,
    technical_score: float,
    speech_score: float
) -> float:
    """
    Weighted scoring formula:
    resumeScore (15%) + atsScore (10%) + matchingScore (20%) +
    backgroundScore (10%) + technicalScore (30%) + speechScore (15%)
    """
    overall = (
        (resume_score * 0.15) +
        (ats_score * 0.10) +
        (matching_score * 0.20) +
        (background_score * 0.10) +
        (technical_score * 0.30) +
        (speech_score * 0.15)
    )
    return round(overall, 1)
