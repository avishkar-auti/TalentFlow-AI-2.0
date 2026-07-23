"""Technical Agent core logic."""
import json
import logging
from typing import Dict, Any, List

from .models import TechnicalEvaluationResult, CodeReview, TechnicalAnswer
from .prompts import TECHNICAL_EVALUATION_PROMPT
from .utils import extract_technical_qa, basic_code_analysis
from .firebase import TechnicalRepository

try:
    from backend.tools.llm_tools import generate_content_groq
except ImportError:
    logging.warning("backend.tools.llm_tools not found. Using mock LLM function.")
    def generate_content_groq(prompt: str, model: str = "llama-3.3-70b") -> str:
        return json.dumps({
            "correctness_score": 85,
            "code_quality_score": 80,
            "problem_solving_score": 90,
            "technical_depth_score": 88,
            "feedback": "Mock feedback."
        })

logger = logging.getLogger(__name__)

class TechnicalAgent:
    """Agent responsible for evaluating technical interviews and code submissions."""
    
    def __init__(self):
        self.repository = TechnicalRepository()
        
    def _compute_overall_score(self, llm_scores: Dict[str, int], qa_analysis: List[TechnicalAnswer], code_reviews: List[CodeReview]) -> int:
        """Compute the final technical score out of 100."""
        # Weighted average of LLM scores
        llm_avg = (
            llm_scores.get('correctness_score', 0) * 0.35 +
            llm_scores.get('problem_solving_score', 0) * 0.30 +
            llm_scores.get('technical_depth_score', 0) * 0.20 +
            llm_scores.get('code_quality_score', 0) * 0.15
        )
        
        # Adjust based on deterministic syntax errors
        penalty = 0
        if any(cr.has_syntax_errors for cr in code_reviews):
            penalty += 15
            
        final_score = int(llm_avg - penalty)
        return max(0, min(100, final_score))

    def process(self, candidate_id: str, interview_id: str) -> TechnicalEvaluationResult:
        """
        Process the transcript and code to generate technical evaluation.
        """
        logger.info(f"Starting technical evaluation for candidate: {candidate_id}, interview: {interview_id}")
        
        # 1. Read data from Firestore
        interview_data = self.repository.get_interview_data(candidate_id, interview_id)
        if not interview_data:
            raise ValueError("Interview data not found.")
            
        transcript = interview_data.get('transcript', '')
        code_submissions = interview_data.get('code_submissions', [])
        expected_keywords = interview_data.get('expected_keywords', ['api', 'database', 'optimization'])
        
        # 2. Python deterministic analysis
        # QA Analysis
        qa_metrics = extract_technical_qa(transcript, expected_keywords)
        qa_analysis = [TechnicalAnswer(
            question="Overall Technical Interview",
            answer=transcript[:100] + "...",
            keyword_match_ratio=qa_metrics['keyword_match_ratio'],
            completeness_score=qa_metrics['completeness_score']
        )]
        
        # Code Analysis
        code_reviews = []
        for sub in code_submissions:
            filename = sub.get('filename', 'unknown.py')
            code = sub.get('code', '')
            c_metrics = basic_code_analysis(code)
            code_reviews.append(CodeReview(
                filename=filename,
                has_syntax_errors=c_metrics['has_syntax_errors'],
                line_count=c_metrics['line_count'],
                basic_quality_score=c_metrics['basic_quality_score']
            ))
            
        # 3. LLM analysis via Groq llama-3.3-70b
        prompt = TECHNICAL_EVALUATION_PROMPT.format(
            candidate_id=candidate_id,
            interview_id=interview_id,
            qa_summary=json.dumps(qa_metrics),
            code_summary=json.dumps([cr.model_dump() for cr in code_reviews]),
            transcript=transcript,
            code_submissions=json.dumps(code_submissions)
        )
        
        logger.info("Calling Groq LLM for technical evaluation...")
        llm_response_text = generate_content_groq(prompt, model="llama-3.3-70b")
        
        try:
            clean_json = llm_response_text.strip().removeprefix('```json').removesuffix('```').strip()
            llm_data = json.loads(clean_json)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise RuntimeError("Invalid response from LLM")
            
        # 4. Compute final technical_score
        technical_score = self._compute_overall_score(llm_data, qa_analysis, code_reviews)
        
        result = TechnicalEvaluationResult(
            candidate_id=candidate_id,
            interview_id=interview_id,
            qa_analysis=qa_analysis,
            code_reviews=code_reviews,
            correctness_score=llm_data.get('correctness_score', 0),
            code_quality_score=llm_data.get('code_quality_score', 0),
            problem_solving_score=llm_data.get('problem_solving_score', 0),
            technical_depth_score=llm_data.get('technical_depth_score', 0),
            technical_score=technical_score,
            llm_feedback=llm_data.get('feedback', '')
        )
        
        # 5. Write to Firestore
        logger.info("Saving technical evaluation to Firestore...")
        save_data = result.model_dump(mode='json')
        self.repository.save_technical_evaluation(candidate_id, interview_id, save_data)
            
        logger.info("Technical evaluation complete.")
        return result
