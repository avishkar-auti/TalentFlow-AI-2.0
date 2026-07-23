def calculate_overall_score(
    resume_score: float,
    ats_score: float,
    matching_score: float,
    background_score: float,
    technical_score: float,
    speech_score: float
) -> float:
    return (
        resume_score * 0.15 +
        ats_score * 0.10 +
        matching_score * 0.20 +
        background_score * 0.10 +
        technical_score * 0.30 +
        speech_score * 0.15
    )

def map_to_recommendation(score: float) -> str:
    if score >= 90:
        return "STRONG_HIRE"
    elif score >= 80:
        return "HIRE"
    elif score >= 65:
        return "MAYBE"
    elif score >= 50:
        return "NO_HIRE"
    else:
        return "STRONG_NO_HIRE"
