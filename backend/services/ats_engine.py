"""Enhanced ATS Scoring Engine — 6-factor candidate-to-job matching."""
import re
import math
from typing import Dict, Any, List, Optional


class ATSEngine:
    """
    6-Factor ATS Score (0-100):
    - Keyword Match    (35%): TF-IDF-like overlap between resume text and job description
    - Skill Overlap    (30%): Exact + fuzzy match of candidate skills vs required_skills
    - Experience Level (15%): Years experience parsed from resume vs job requirement
    - Education Match  (10%): Degree level match
    - Section Complete  (5%): Presence of summary, experience, education, skills, contact
    - Formatting Quality(5%): ATS-friendly format check
    """

    EDUCATION_LEVELS = {
        'phd': 5, 'doctorate': 5,
        'master': 4, 'masters': 4, 'msc': 4, 'ms ': 4, 'mba': 4, 'mtech': 4, 'm.tech': 4,
        'bachelor': 3, 'bachelors': 3, 'bsc': 3, 'btech': 3, 'b.tech': 3, 'be ': 3,
        'associate': 2, 'diploma': 1, 'high school': 0
    }

    def compute_score(self, resume_text: str, job_data: dict, parsed_analysis: dict) -> dict:
        """Return dict with total_score (0-100) + breakdown of all 6 factors."""
        resume_text_lower = (resume_text or "").lower()

        keyword_score = self._keyword_match(resume_text_lower, job_data)
        skill_score = self._skill_overlap(parsed_analysis.get('skills', []), job_data)
        exp_score = self._experience_match(resume_text_lower, parsed_analysis, job_data)
        edu_score = self._education_match(resume_text_lower, parsed_analysis, job_data)
        section_score = self._section_completeness(resume_text_lower, parsed_analysis)
        format_score = self._formatting_quality(resume_text)

        total = (
            keyword_score * 0.35 +
            skill_score   * 0.30 +
            exp_score     * 0.15 +
            edu_score     * 0.10 +
            section_score * 0.05 +
            format_score  * 0.05
        )
        total = round(min(float(total), 100.0), 1)

        return {
            'total_score': total,
            'breakdown': {
                'keyword_match':        round(float(keyword_score), 1),
                'skill_overlap':        round(float(skill_score), 1),
                'experience_match':     round(float(exp_score), 1),
                'education_match':      round(float(edu_score), 1),
                'section_completeness': round(float(section_score), 1),
                'formatting_quality':   round(float(format_score), 1),
            },
            'weights': {
                'keyword_match': 35,
                'skill_overlap': 30,
                'experience_match': 15,
                'education_match': 10,
                'section_completeness': 5,
                'formatting_quality': 5,
            },
            'is_shortlistable': total >= 70,
        }

    # ── Factor 1: Keyword Match ─────────────────────────────────────────────────

    def _keyword_match(self, resume_lower: str, job_data: dict) -> float:
        req = job_data.get('requirements', {}) or {}
        skills_list = req.get('skills', []) if isinstance(req, dict) else []
        job_desc = (
            (job_data.get('description') or '') + ' ' +
            ' '.join(skills_list) + ' ' +
            (job_data.get('title') or '') + ' ' +
            (job_data.get('department') or '')
        ).lower()

        if len(job_desc.strip()) < 10:
            return 75.0  # no job description → neutral score

        stop_words = {
            'the', 'a', 'an', 'is', 'in', 'it', 'of', 'to', 'and', 'or', 'for',
            'with', 'on', 'at', 'as', 'by', 'be', 'are', 'was', 'were', 'from',
            'this', 'that', 'have', 'has', 'will', 'you', 'we', 'our', 'their',
            'they', 'can', 'may', 'must', 'should', 'would', 'could', 'work',
            'team', 'join', 'build', 'using', 'used', 'use', 'new', 'provide',
            'ability', 'experience', 'role', 'required', 'strong', 'good', 'best'
        }

        resume_tokens = set(re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.\-_]{1,}\b', resume_lower))
        job_tokens = set(re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.\-_]{1,}\b', job_desc))
        job_keywords = {t for t in job_tokens if t not in stop_words and len(t) > 2}

        if not job_keywords:
            return 75.0

        matched = resume_tokens & job_keywords
        raw = (len(matched) / len(job_keywords)) * 100
        # Apply 1.4x multiplier since TF-IDF weights common technical terms more
        return min(raw * 1.4, 100.0)

    # ── Factor 2: Skill Overlap ─────────────────────────────────────────────────

    def _skill_overlap(self, resume_skills: list, job_data: dict) -> float:
        req = job_data.get('requirements', {}) or {}
        if isinstance(req, dict):
            required = [str(s).lower().strip() for s in req.get('skills', [])]
        else:
            required = []

        # Also check required_skills at top level
        top_skills = [str(s).lower().strip() for s in (job_data.get('required_skills') or [])]
        required = list(set(required + top_skills))

        if not required:
            return 70.0  # no skill requirement → neutral

        resume_skill_lower = [str(s).lower().strip() for s in (resume_skills or [])]

        def fuzzy_match(req_skill: str, cand_skills: list) -> bool:
            for cs in cand_skills:
                if req_skill in cs or cs in req_skill:
                    return True
                # Handle abbreviations (e.g. 'js' matches 'javascript')
                if len(req_skill) <= 3 and req_skill in cs:
                    return True
            return False

        matched = sum(1 for s in required if fuzzy_match(s, resume_skill_lower))
        raw = (matched / len(required)) * 100
        return min(raw * 1.2, 100.0)

    # ── Factor 3: Experience Match ──────────────────────────────────────────────

    def _experience_match(self, resume_lower: str, parsed: dict, job_data: dict) -> float:
        # Extract years of experience from resume
        year_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)',
            r'(\d+)\s+(?:years?|yrs?)',
            r'(\d{4})\s*[-–]\s*(?:present|current|now|\d{4})',  # date range
        ]
        all_years = []
        for pat in year_patterns:
            matches = re.findall(pat, resume_lower)
            for m in matches:
                try:
                    y = int(m)
                    if 1 <= y <= 40:
                        all_years.append(y)
                    elif 2000 <= y <= 2026:
                        # It's a year range start, estimate years
                        all_years.append(2026 - y)
                except:
                    pass

        candidate_years = max(all_years, default=1)

        # Get required years from job
        req = job_data.get('requirements', {}) or {}
        req_experience = req.get('experience', '') if isinstance(req, dict) else ''
        exp_level = (job_data.get('experience_level') or '').lower()

        # Map experience_level to years
        level_map = {'junior': 1, 'entry': 1, 'mid': 3, 'senior': 5, 'lead': 7, 'principal': 9}
        required_years = level_map.get(exp_level, 2)

        # Also parse from experience text
        req_yr_matches = re.findall(r'(\d+)', str(req_experience))
        if req_yr_matches:
            required_years = max(required_years, int(req_yr_matches[0]))

        if candidate_years >= required_years:
            bonus = min((candidate_years - required_years) * 4, 20)
            return min(80.0 + bonus, 100.0)
        elif candidate_years > 0:
            ratio = candidate_years / max(required_years, 1)
            return max(25.0, ratio * 85)
        return 35.0

    # ── Factor 4: Education Match ───────────────────────────────────────────────

    def _education_match(self, resume_lower: str, parsed: dict, job_data: dict) -> float:
        candidate_level = 0
        for degree_kw, level in sorted(self.EDUCATION_LEVELS.items(), key=lambda x: -x[1]):
            if degree_kw in resume_lower:
                candidate_level = max(candidate_level, level)

        req = job_data.get('requirements', {}) or {}
        req_edu = str(req.get('education', 'bachelor') if isinstance(req, dict) else 'bachelor').lower()
        required_level = 3  # default: bachelor

        for degree_kw, level in self.EDUCATION_LEVELS.items():
            if degree_kw in req_edu:
                required_level = level
                break

        if candidate_level >= required_level:
            return 100.0
        elif candidate_level > 0:
            return max(40.0, (candidate_level / max(required_level, 1)) * 100)
        # No education found — assume some education
        return 55.0

    # ── Factor 5: Section Completeness ─────────────────────────────────────────

    def _section_completeness(self, resume_lower: str, parsed: dict) -> float:
        section_checks = {
            'contact': any(k in resume_lower for k in ['@', 'email', 'phone', 'mobile', 'linkedin', 'github']),
            'summary': any(k in resume_lower for k in ['summary', 'objective', 'profile', 'about me', 'overview']),
            'experience': any(k in resume_lower for k in ['experience', 'employment', 'work history', 'career', 'position']),
            'education': any(k in resume_lower for k in ['education', 'degree', 'university', 'college', 'institute', 'school']),
            'skills': any(k in resume_lower for k in ['skill', 'technologies', 'tools', 'expertise', 'competenc', 'proficien']),
        }
        score = sum(1 for v in section_checks.values() if v) / len(section_checks) * 100

        # Bonus for optional sections
        if any(k in resume_lower for k in ['project', 'portfolio', 'certification', 'award', 'achievement']):
            score = min(score + 10, 100)

        return score

    # ── Factor 6: Formatting Quality ───────────────────────────────────────────

    def _formatting_quality(self, resume_text: str) -> float:
        score = 100.0
        text = resume_text or ''

        # Too short (less than 200 chars)
        if len(text) < 200:
            score -= 50
        elif len(text) < 500:
            score -= 20

        # Too long (> 8000 chars = ~4+ pages)
        if len(text) > 8000:
            score -= 15

        # Table-heavy (ATS can't parse tables)
        if text.count('|') > 15:
            score -= 20

        # Graphics/columns indicator (many consecutive spaces)
        multi_space = len(re.findall(r' {5,}', text))
        if multi_space > 20:
            score -= 15

        return max(score, 10.0)
