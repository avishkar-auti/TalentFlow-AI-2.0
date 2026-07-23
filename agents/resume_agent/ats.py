"""
ATS Scanner & AST Formatting Evaluator.
Calculates keyword density, missing keywords, ATS formatting compatibility, and overall resume quality score.
"""
import re
import logging
from typing import Dict, Any, List, Tuple, Set

logger = logging.getLogger(__name__)

class ATSScanner:
    """Real ATS Scanning Engine for Resume AST analysis."""

    @staticmethod
    def scan_resume(
        extracted_text: str,
        ast_data: Dict[str, Any],
        parsed_skills: List[str],
        job_requirements: List[str]
    ) -> Dict[str, Any]:
        """
        Scans extracted resume text and AST structure against job requirements.
        Returns ATS Score, missing keywords, formatting flags, and quality score breakdown.
        """
        clean_text_lower = extracted_text.lower()
        
        # 1. Normalize job requirements into target keywords
        target_keywords: Set[str] = set()
        for req in job_requirements:
            # Extract individual tech/skill terms
            words = re.findall(r'\b[A-Za-z0-9+#\.\-]{2,}\b', req.lower())
            for w in words:
                if len(w) > 2 and w not in {'and', 'for', 'with', 'the', 'must', 'have', 'years', 'experience'}:
                    target_keywords.add(w)

        # Include candidate's parsed skills as uppercase/normalized
        candidate_skill_set = {s.lower() for s in parsed_skills}

        matched_keywords: List[str] = []
        missing_keywords: List[str] = []

        for kw in target_keywords:
            if kw in clean_text_lower or kw in candidate_skill_set:
                matched_keywords.append(kw)
            else:
                missing_keywords.append(kw)

        # Calculate Keyword / ATS Overlap Score (0 - 100)
        total_target = max(len(target_keywords), 1)
        keyword_match_ratio = len(matched_keywords) / total_target
        ats_score = min(round(keyword_match_ratio * 100, 1), 100.0)

        # If no explicit job requirements were provided, fallback to standard skill density formula
        if len(job_requirements) == 0:
            ats_score = min(round(len(parsed_skills) * 8.5, 1), 92.0)
            missing_keywords = []

        # 2. ATS Formatting & Layout Analysis
        formatting_flags: List[str] = []
        formatting_penalty: float = 0.0

        total_pages = ast_data.get("total_pages", 1)
        if total_pages > 3:
            formatting_flags.append(f"Excessive page count ({total_pages} pages). Ideal resume is 1-2 pages.")
            formatting_penalty += 10.0

        if ast_data.get("has_scanned_text"):
            formatting_flags.append("Scanned image PDF detected. Text is not easily readable by standard ATS parsers.")
            formatting_penalty += 35.0

        fonts = ast_data.get("fonts_used", [])
        if len(fonts) > 6:
            formatting_flags.append(f"Too many fonts used ({len(fonts)} fonts). May reduce ATS parser consistency.")
            formatting_penalty += 5.0

        ats_formatting_score = max(round(100.0 - formatting_penalty, 1), 0.0)

        # 3. Overall Resume Quality Score
        completeness_points = 0
        if len(parsed_skills) >= 5: completeness_points += 25
        elif len(parsed_skills) >= 2: completeness_points += 15
        
        if len(extracted_text) > 300: completeness_points += 25
        if re.search(r'@\w+\.\w+', extracted_text): completeness_points += 25 # Has email
        if re.search(r'\b(experience|work|history)\b', clean_text_lower): completeness_points += 25

        resume_quality_score = round((ats_score * 0.5) + (completeness_points * 0.3) + (ats_formatting_score * 0.2), 1)

        return {
            "ats_score": float(ats_score),
            "resume_quality_score": float(resume_quality_score),
            "ats_formatting_score": float(ats_formatting_score),
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords[:10], # Top missing keywords
            "formatting_flags": formatting_flags
        }
