"""Domain models for Speech Agent."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class FillerWordAnalysis(BaseModel):
    """Analysis of filler words used in speech."""
    counts: Dict[str, int] = Field(default_factory=dict, description="Count of each filler word")
    total_fillers: int = Field(default=0, description="Total number of filler words")
    fillers_per_minute: float = Field(default=0.0, description="Filler words per minute")

class FluencyMetrics(BaseModel):
    """Metrics related to speech fluency."""
    word_count: int = Field(default=0, description="Total words spoken")
    speaking_pace: float = Field(default=0.0, description="Words per minute")
    vocabulary_diversity: float = Field(default=0.0, description="Type-token ratio (unique words / total words)")

class SpeechAnalysisResult(BaseModel):
    """Final result of the speech analysis."""
    candidate_id: str
    interview_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Deterministic metrics
    fluency: FluencyMetrics
    filler_words: FillerWordAnalysis
    
    # LLM-based metrics
    communication_clarity_score: int = Field(ge=0, le=100)
    confidence_score: int = Field(ge=0, le=100)
    articulation_score: int = Field(ge=0, le=100)
    overall_fluency_score: int = Field(ge=0, le=100)
    
    # Final computed score
    speech_score: int = Field(ge=0, le=100)
    
    llm_feedback: str = Field(default="", description="Detailed qualitative feedback from LLM")
