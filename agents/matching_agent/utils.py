import re
from typing import List, Set, Tuple

SKILL_SYNONYMS = {
    'js': 'javascript',
    'ts': 'typescript',
    'ml': 'machine learning',
    'ai': 'artificial intelligence',
    'react': 'react.js',
    'node': 'node.js',
    'vue': 'vue.js',
    'k8s': 'kubernetes',
    'aws': 'amazon web services',
    'gcp': 'google cloud',
    'go': 'golang',
}

def normalize_skill_name(skill: str) -> str:
    s = skill.lower().strip()
    return SKILL_SYNONYMS.get(s, s)

def compute_skill_overlap(candidate_skills: List[str], required_skills: List[str]) -> Tuple[float, List[str]]:
    cand_norm = {normalize_skill_name(s) for s in candidate_skills}
    req_norm = {normalize_skill_name(s) for s in required_skills}
    
    if not req_norm:
        return 1.0, []
        
    overlap = cand_norm.intersection(req_norm)
    missing = req_norm - cand_norm
    
    score = len(overlap) / len(req_norm)
    return score, list(missing)

def compute_experience_match(candidate_years: float, required_years: float) -> float:
    if required_years == 0:
        return 1.0
    if candidate_years >= required_years:
        return 1.0
    
    return max(0.0, candidate_years / required_years)

DEGREE_LEVELS = {
    'none': 0,
    'high school': 1,
    'associate': 2,
    'bachelor': 3,
    'master': 4,
    'phd': 5,
    'doctorate': 5
}

def normalize_degree(degree: str) -> int:
    d = degree.lower()
    for k, v in DEGREE_LEVELS.items():
        if k in d:
            return v
    return 0

def compute_education_match(candidate_degree: str, required_degree: str) -> float:
    req_level = normalize_degree(required_degree)
    if req_level == 0:
        return 1.0
        
    cand_level = normalize_degree(candidate_degree)
    if cand_level >= req_level:
        return 1.0
    
    return max(0.0, cand_level / req_level)

def compute_location_match(candidate_location: str, required_location: str) -> float:
    if not required_location or required_location.lower() == 'remote':
        return 1.0
    if not candidate_location:
        return 0.0
        
    return 1.0 if candidate_location.lower().strip() == required_location.lower().strip() else 0.0

def weighted_score(scores: dict, weights: dict) -> float:
    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0.0
    
    weighted_sum = sum(scores.get(k, 0.0) * w for k, w in weights.items())
    return weighted_sum / total_weight
