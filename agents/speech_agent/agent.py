"""Speech Agent core logic."""
import json
import logging
from typing import Dict, Any

from .models import SpeechAnalysisResult, FillerWordAnalysis, FluencyMetrics
from .prompts import SPEECH_ANALYSIS_PROMPT
from .utils import count_filler_words, calculate_speaking_pace, vocabulary_diversity, _clean_text
from .firebase import SpeechRepository

try:
    from backend.tools.llm_tools import generate_content_gemini
except ImportError:
    logging.warning("backend.tools.llm_tools not found. Using mock LLM function.")
    def generate_content_gemini(prompt: str) -> str:
        return json.dumps({
            "communication_clarity_score": 85,
            "confidence_score": 80,
            "articulation_score": 75,
            "overall_fluency_score": 82,
            "feedback": "Mock feedback."
        })

logger = logging.getLogger(__name__)

class SpeechAgent:
    """Agent responsible for analyzing candidate speech transcripts."""
    
    def __init__(self):
        self.repository = SpeechRepository()
        
    def _compute_overall_score(self, llm_scores: Dict[str, int], fluency: FluencyMetrics, fillers: FillerWordAnalysis) -> int:
        """Compute the final speech score out of 100 based on all metrics."""
        # Weighted average of LLM scores
        llm_avg = (
            llm_scores.get('communication_clarity_score', 0) * 0.3 +
            llm_scores.get('confidence_score', 0) * 0.3 +
            llm_scores.get('articulation_score', 0) * 0.2 +
            llm_scores.get('overall_fluency_score', 0) * 0.2
        )
        
        # Penalize for excessive fillers (e.g., > 5 per minute)
        filler_penalty = min(20, max(0, (fillers.fillers_per_minute - 5) * 2))
        
        # Reward vocabulary diversity (TTR usually between 0.3 and 0.6)
        vocab_bonus = 0
        if fluency.vocabulary_diversity > 0.5:
            vocab_bonus = 5
        elif fluency.vocabulary_diversity < 0.3:
            vocab_bonus = -5
            
        final_score = int(llm_avg - filler_penalty + vocab_bonus)
        return max(0, min(100, final_score))

    def process(self, candidate_id: str, interview_id: str) -> SpeechAnalysisResult:
        """
        Process the interview transcript and generate speech analysis.
        
        Args:
            candidate_id: The candidate ID.
            interview_id: The interview ID.
            
        Returns:
            SpeechAnalysisResult containing the full evaluation.
            
        Raises:
            ValueError: If transcript cannot be found or is empty.
        """
        logger.info(f"Starting speech analysis for candidate: {candidate_id}, interview: {interview_id}")
        
        # 1. Read transcript from Firestore
        interview_data = self.repository.get_interview_transcript(candidate_id, interview_id)
        if not interview_data or 'transcript' not in interview_data:
            logger.error("Transcript not found.")
            raise ValueError("Transcript not found for the given interview.")
            
        transcript = interview_data['transcript']
        duration_seconds = interview_data.get('duration_seconds', 300) # Default 5 mins if not provided
        
        # 2. Python deterministic analysis
        clean_words = _clean_text(transcript).split()
        word_count = len(clean_words)
        
        filler_counts, total_fillers = count_filler_words(transcript)
        speaking_pace = calculate_speaking_pace(word_count, duration_seconds)
        vocab_div = vocabulary_diversity(transcript)
        
        fillers_per_min = calculate_speaking_pace(total_fillers, duration_seconds)
        
        filler_analysis = FillerWordAnalysis(
            counts=filler_counts,
            total_fillers=total_fillers,
            fillers_per_minute=fillers_per_min
        )
        
        fluency_metrics = FluencyMetrics(
            word_count=word_count,
            speaking_pace=speaking_pace,
            vocabulary_diversity=vocab_div
        )
        
        # 3. LLM analysis via Gemini
        prompt = SPEECH_ANALYSIS_PROMPT.format(
            candidate_id=candidate_id,
            interview_id=interview_id,
            word_count=word_count,
            speaking_pace=speaking_pace,
            vocab_diversity=vocab_div,
            total_fillers=total_fillers,
            fillers_per_minute=fillers_per_min,
            transcript=transcript
        )
        
        logger.info("Calling LLM for speech analysis...")
        llm_response_text = generate_content_gemini(prompt)
        
        try:
            # Strip markdown json blocks if present
            clean_json = llm_response_text.strip().removeprefix('```json').removesuffix('```').strip()
            llm_data = json.loads(clean_json)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise RuntimeError("Invalid response from LLM")
            
        # 4. Compute final speech_score
        speech_score = self._compute_overall_score(llm_data, fluency_metrics, filler_analysis)
        
        result = SpeechAnalysisResult(
            candidate_id=candidate_id,
            interview_id=interview_id,
            fluency=fluency_metrics,
            filler_words=filler_analysis,
            communication_clarity_score=llm_data.get('communication_clarity_score', 0),
            confidence_score=llm_data.get('confidence_score', 0),
            articulation_score=llm_data.get('articulation_score', 0),
            overall_fluency_score=llm_data.get('overall_fluency_score', 0),
            speech_score=speech_score,
            llm_feedback=llm_data.get('feedback', '')
        )
        
        # 5. Write to Firestore
        logger.info("Saving analysis to Firestore...")
        # Dump model to dict
        save_data = result.model_dump(mode='json')
        success = self.repository.save_speech_analysis(candidate_id, interview_id, save_data)
        
        if not success:
            logger.warning("Failed to save analysis to database, but returning results anyway.")
            
        logger.info("Speech analysis complete.")
        return result
