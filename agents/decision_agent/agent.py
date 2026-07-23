"""
Decision Agent Orchestrator.
Aggregates all component scores via deterministic formula and produces business hiring decision reports.
"""
import logging
from typing import Dict, Any
from .score_engine import calculate_overall_score
from .recommendation import map_to_recommendation
from .report import generate_business_summary
from .firebase import fetch_all_candidate_agent_data, save_decision_result

logger = logging.getLogger(__name__)

class DecisionAgent:
    """Production Decision Agent for TalentFlow-AI."""

    async def process(self, candidate_id: str, job_id: str) -> Dict[str, Any]:
        """
        Calculates final hiring recommendation and summary report:
        1. Fetch all agent outputs from Firestore
        2. Execute weighted scoring formula
        3. Map recommendation (STRONG_HIRE, HIRE, MAYBE, NO_HIRE, STRONG_NO_HIRE)
        4. Generate plain-language AI summary
        5. Persist to Firestore
        """
        logger.info(f"Generating hiring decision report for candidate_id={candidate_id}")

        all_data = await fetch_all_candidate_agent_data(candidate_id)
        
        resume_doc = all_data.get("resume", {})
        matching_doc = all_data.get("matching", {})
        background_doc = all_data.get("background", {})
        technical_doc = all_data.get("technical", {})
        speech_doc = all_data.get("speech", {})
        cand_doc = all_data.get("candidate", {})

        # Extract scores with default fallbacks
        resume_score = float(resume_doc.get("score", {}).get("resume_score", cand_doc.get("resumeQualityScore", 85.0)))
        ats_score = float(resume_doc.get("score", {}).get("ats_score", cand_doc.get("atsScore", 88.0)))
        matching_score = float(matching_doc.get("overallMatch", cand_doc.get("overallMatch", 85.0)))
        background_score = float(background_doc.get("overall_score", 95.0))
        technical_score = float(technical_doc.get("technical_score", 88.0))
        speech_score = float(speech_doc.get("speech_score", 85.0))

        overall_score = calculate_overall_score(
            resume_score=resume_score,
            ats_score=ats_score,
            matching_score=matching_score,
            background_score=background_score,
            technical_score=technical_score,
            speech_score=speech_score
        )

        recommendation = map_to_recommendation(overall_score)
        
        scores_map = {
            "resumeScore": resume_score,
            "atsScore": ats_score,
            "matchingScore": matching_score,
            "backgroundScore": background_score,
            "technicalScore": technical_score,
            "speechScore": speech_score
        }

        candidate_name = cand_doc.get("name", "Candidate")
        job_title = cand_doc.get("jobTitle", "Target Role")

        summary_report = generate_business_summary(
            candidate_name=candidate_name,
            job_title=job_title,
            overall_score=overall_score,
            recommendation=recommendation,
            scores=scores_map
        )

        decision_result = {
            "candidateId": candidate_id,
            "jobId": job_id,
            "overallScore": overall_score,
            "recommendation": recommendation,
            "scores": scores_map,
            "remarks": summary_report["summary"],
            "strengths": summary_report["strengths"],
            "concerns": summary_report["concerns"],
            "generatedAt": "now"
        }

        await save_decision_result(candidate_id, decision_result)

        logger.info(f"Hiring decision generated for {candidate_id}. Overall: {overall_score}%, Recommendation: {recommendation}")
        return decision_result
