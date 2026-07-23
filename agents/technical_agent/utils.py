"""Utility functions for Technical Agent analysis."""
import ast
from typing import Dict, List, Any

def extract_technical_qa(transcript: str, expected_keywords: List[str]) -> Dict[str, Any]:
    """
    Extract technical Q&A metrics based on keyword presence and completeness.
    
    Args:
        transcript: The full text transcript.
        expected_keywords: List of expected technical keywords.
        
    Returns:
        Dictionary containing keyword match ratio and completeness score.
    """
    if not transcript:
        return {"keyword_match_ratio": 0.0, "completeness_score": 0.0}
        
    transcript_lower = transcript.lower()
    
    matched = sum(1 for kw in expected_keywords if kw.lower() in transcript_lower)
    match_ratio = matched / len(expected_keywords) if expected_keywords else 0.0
    
    # Rough heuristic for completeness based on length and keywords
    words = len(transcript.split())
    completeness = min(1.0, (words / 200) * 0.5 + match_ratio * 0.5)
    
    return {
        "keyword_match_ratio": round(match_ratio, 2),
        "completeness_score": round(completeness, 2)
    }

def basic_code_analysis(code_string: str) -> Dict[str, Any]:
    """
    Perform basic deterministic static analysis on a code string (assuming Python).
    
    Args:
        code_string: The source code to analyze.
        
    Returns:
        Dictionary with code metrics.
    """
    lines = code_string.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    
    metrics = {
        "has_syntax_errors": False,
        "line_count": len(non_empty_lines),
        "basic_quality_score": 1.0
    }
    
    if not code_string.strip():
        metrics["basic_quality_score"] = 0.0
        return metrics
        
    try:
        ast.parse(code_string)
    except SyntaxError:
        metrics["has_syntax_errors"] = True
        metrics["basic_quality_score"] = 0.2
        return metrics
        
    # Check basic formatting / quality heuristics
    long_lines = sum(1 for line in non_empty_lines if len(line) > 100)
    if long_lines > 0:
        penalty = min(0.5, (long_lines / len(non_empty_lines)))
        metrics["basic_quality_score"] -= penalty
        
    return metrics
