"""
Experience Match & Career Timeline Evaluator.
"""
import re
from typing import Any, Dict, List

def parse_years(exp_str: str) -> float:
    match = re.search(r'(\d+)', str(exp_str))
    if match:
        return float(match.group(1))
    return 1.0

def evaluate_experience_match(candidate_exp: Any, required_exp: Any) -> float:
    cand_years = parse_years(candidate_exp)
    req_years = parse_years(required_exp)

    if req_years <= 0:
        return 100.0

    if cand_years >= req_years:
        return 100.0
    else:
        ratio = cand_years / req_years
        return max(round(ratio * 100.0, 1), 40.0)
