"""
Recommendation Mapping Engine.
"""
def map_to_recommendation(overall_score: float) -> str:
    """
    Deterministic recommendation mapping:
    >= 90: STRONG_HIRE
    >= 80: HIRE
    >= 65: MAYBE
    >= 50: NO_HIRE
    < 50: STRONG_NO_HIRE
    """
    if overall_score >= 90.0:
        return "STRONG_HIRE"
    elif overall_score >= 80.0:
        return "HIRE"
    elif overall_score >= 65.0:
        return "MAYBE"
    elif overall_score >= 50.0:
        return "NO_HIRE"
    else:
        return "STRONG_NO_HIRE"
