"""
Skill Overlap & Synonym Normalization Module.
"""
import re
from typing import List, Tuple, Set

SKILL_SYNONYMS = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "fastapi": "fastapi",
    "react.js": "react",
    "reactjs": "react",
    "node": "node.js",
    "nodejs": "node.js",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "k8s": "kubernetes",
    "aws": "amazon web services",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "cv": "computer vision",
    "nlp": "natural language processing"
}

def normalize_skill(skill_name: str) -> str:
    cleaned = skill_name.strip().lower()
    return SKILL_SYNONYMS.get(cleaned, cleaned)

def evaluate_skill_match(candidate_skills: List[str], required_skills: List[str]) -> Tuple[float, List[str], List[str]]:
    """
    Evaluates skill set overlap between candidate and job requirements.
    Returns (match_percentage, matched_skills, missing_skills).
    """
    if not required_skills:
        return 100.0, candidate_skills, []

    cand_set = {normalize_skill(s) for s in candidate_skills}
    req_set = {normalize_skill(s) for s in required_skills}

    matched = []
    missing = []

    for req in req_set:
        # Exact or substring match
        if any(req == cand or req in cand or cand in req for cand in cand_set):
            matched.append(req)
        else:
            missing.append(req)

    match_percentage = min(round((len(matched) / max(len(req_set), 1)) * 100.0, 1), 100.0)
    return match_percentage, matched, missing
