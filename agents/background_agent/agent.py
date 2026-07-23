import json
from typing import Dict, Any, List
from .models import BackgroundCheckResult, BackgroundCheck, CheckStatus, CheckSeverity
from .firebase import firebase_client
from .utils import (
    validate_experience_timeline,
    validate_education,
    check_skill_plausibility,
    detect_red_flags,
    validate_contact_info
)
from .prompts import CONSISTENCY_CHECK_PROMPT

class BackgroundAgent:
    def __init__(self):
        # In a real setup, inject LLM client here
        pass

    async def _call_llm_for_inconclusive(self, information: str, context: str) -> Dict[str, Any]:
        """Calls the lightweight LLM (llama-3.1-8b-instant) for inconclusive checks."""
        # Mock LLM call returning forced JSON
        # In real code, use llm_tools or equivalent
        return {
            "is_valid": True,
            "concerns": [],
            "confidence": 0.9
        }

    async def process(self, candidate_id: str, job_id: str) -> BackgroundCheckResult:
        # Step 1: Check cache first
        cached = await firebase_client.get_cached_background_check(candidate_id, job_id)
        if cached:
            return BackgroundCheckResult(**cached)

        # Step 2: Read candidate data + resume analysis
        candidate = await firebase_client.get_candidate(candidate_id)
        if not candidate:
            raise ValueError("Candidate not found")
            
        resume_analysis = await firebase_client.get_candidate_resume_analysis(candidate_id)
        if not resume_analysis:
            resume_analysis = {}

        checks: List[BackgroundCheck] = []
        flags: List[str] = []
        concerns: List[str] = []

        # Step 3: Run ALL checks in Python
        
        # Duplicate detection
        is_duplicate = await firebase_client.check_duplicates(
            candidate.get("email", ""), candidate.get("phone", ""), job_id
        )
        if is_duplicate:
            checks.append(BackgroundCheck(
                check_name="Duplicate Detection",
                status=CheckStatus.FAILED,
                detail="Candidate already applied for this job.",
                severity=CheckSeverity.HIGH
            ))
        else:
            checks.append(BackgroundCheck(
                check_name="Duplicate Detection",
                status=CheckStatus.PASSED,
                detail="No duplicates found.",
                severity=CheckSeverity.LOW
            ))

        # Contact info validation
        contact_valid, contact_issues = validate_contact_info(
            candidate.get("email", ""), candidate.get("phone", "")
        )
        if not contact_valid:
            checks.append(BackgroundCheck(
                check_name="Contact Info Validation",
                status=CheckStatus.FAILED,
                detail="; ".join(contact_issues),
                severity=CheckSeverity.MEDIUM
            ))
        else:
            checks.append(BackgroundCheck(
                check_name="Contact Info Validation",
                status=CheckStatus.PASSED,
                detail="Contact info is valid.",
                severity=CheckSeverity.LOW
            ))

        # Experience consistency
        exp_valid, exp_issues = validate_experience_timeline(resume_analysis.get("experiences", []))
        if not exp_valid:
             checks.append(BackgroundCheck(
                check_name="Experience Consistency",
                status=CheckStatus.WARNING, # Or INCONCLUSIVE
                detail="; ".join(exp_issues),
                severity=CheckSeverity.MEDIUM
            ))
        else:
             checks.append(BackgroundCheck(
                check_name="Experience Consistency",
                status=CheckStatus.PASSED,
                detail="Timeline looks consistent.",
                severity=CheckSeverity.LOW
            ))

        # Education verification
        edu_valid, edu_issues = validate_education(resume_analysis.get("education", []))
        if not edu_valid:
             checks.append(BackgroundCheck(
                check_name="Education Verification",
                status=CheckStatus.WARNING,
                detail="; ".join(edu_issues),
                severity=CheckSeverity.MEDIUM
            ))
        else:
            # Let's say we have an inconclusive one to demonstrate LLM usage
            checks.append(BackgroundCheck(
                check_name="Education Verification",
                status=CheckStatus.INCONCLUSIVE,
                detail="University name is ambiguous.",
                severity=CheckSeverity.LOW
            ))

        # Skills plausibility
        # Estimate years of exp
        years = len(resume_analysis.get("experiences", [])) * 2 # Mock
        skills = resume_analysis.get("skills", [])
        skills_valid, skills_issues = check_skill_plausibility(skills, years)
        if not skills_valid:
            checks.append(BackgroundCheck(
                check_name="Skills Plausibility",
                status=CheckStatus.WARNING,
                detail="; ".join(skills_issues),
                severity=CheckSeverity.MEDIUM
            ))
        else:
            checks.append(BackgroundCheck(
                check_name="Skills Plausibility",
                status=CheckStatus.PASSED,
                detail="Skills align with experience.",
                severity=CheckSeverity.LOW
            ))

        # Red flags
        detected_flags = detect_red_flags(resume_analysis)
        if detected_flags:
            flags.extend(detected_flags)
            checks.append(BackgroundCheck(
                check_name="Red Flag Detection",
                status=CheckStatus.WARNING,
                detail="Red flags detected.",
                severity=CheckSeverity.HIGH
            ))
        else:
             checks.append(BackgroundCheck(
                check_name="Red Flag Detection",
                status=CheckStatus.PASSED,
                detail="No obvious red flags.",
                severity=CheckSeverity.LOW
            ))

        # Step 4: ONLY for inconclusive checks, use LLM
        for i, check in enumerate(checks):
            if check.status == CheckStatus.INCONCLUSIVE:
                llm_res = await self._call_llm_for_inconclusive(
                    information=check.detail,
                    context=json.dumps(resume_analysis)
                )
                if llm_res.get("is_valid"):
                    checks[i].status = CheckStatus.PASSED
                    checks[i].detail += " (Verified by AI)"
                else:
                    checks[i].status = CheckStatus.WARNING
                    checks[i].detail += " (AI Concerns: " + ", ".join(llm_res.get("concerns", [])) + ")"
                    concerns.extend(llm_res.get("concerns", []))

        # Step 5: Compute background_score
        total_checks = len(checks)
        passed_checks = sum(1 for c in checks if c.status == CheckStatus.PASSED)
        score = (passed_checks / total_checks) * 100 if total_checks > 0 else 100.0
        
        # Penalties
        for f in flags:
            score -= 10
        score = max(0.0, score)

        is_clear = score >= 90.0 and not flags and not concerns

        result = BackgroundCheckResult(
            overall_score=score,
            checks=checks,
            flags=flags,
            concerns=concerns,
            is_clear=is_clear
        )

        # Step 6: Write to Firestore
        await firebase_client.save_background_check(candidate_id, result.dict())

        # Step 7: Return
        return result
