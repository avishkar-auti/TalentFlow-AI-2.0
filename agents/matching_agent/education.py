"""
Education Degree Rank & Institution Evaluator.
"""
from typing import Any, List

DEGREE_RANKS = {
    "phd": 4,
    "doctorate": 4,
    "master": 3,
    "m.s": 3,
    "m.tech": 3,
    "bachelor": 2,
    "b.s": 2,
    "b.tech": 2,
    "associate": 1,
    "high school": 0
}

def parse_degree_rank(edu_input: Any) -> int:
    text = str(edu_input).lower()
    for degree, rank in DEGREE_RANKS.items():
        if degree in text:
            return rank
    return 2  # Default to Bachelor level

def evaluate_education_match(candidate_edu: Any, required_edu: Any) -> float:
    cand_rank = parse_degree_rank(candidate_edu)
    req_rank = parse_degree_rank(required_edu)

    if cand_rank >= req_rank:
        return 100.0
    elif cand_rank == req_rank - 1:
        return 80.0
    else:
        return 60.0
