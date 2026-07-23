"""Domain models for Technical Agent."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class TechnicalAnswer(BaseModel):
    """Analysis of a specific technical question/answer."""
    question: str
    answer: str
    keyword_match_ratio: float = Field(default=0.0)
    completeness_score: float = Field(default=0.0)
    
class CodeReview(BaseModel):
    """Analysis of a code submission."""
    filename: str
    has_syntax_errors: bool = Field(default=False)
    line_count: int = Field(default=0)
    basic_quality_score: float = Field(default=0.0)

class TechnicalEvaluationResult(BaseModel):
    """Final result of the technical evaluation."""
    candidate_id: str
    interview_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Deterministic metrics
    qa_analysis: List[TechnicalAnswer] = Field(default_factory=list)
    code_reviews: List[CodeReview] = Field(default_factory=list)
    
    # LLM-based metrics (Groq llama-3.3-70b)
    correctness_score: int = Field(ge=0, le=100)
    code_quality_score: int = Field(ge=0, le=100)
    problem_solving_score: int = Field(ge=0, le=100)
    technical_depth_score: int = Field(ge=0, le=100)
    
    # Final computed score
    technical_score: int = Field(ge=0, le=100)
    
    llm_feedback: str = Field(default="", description="Detailed qualitative feedback from LLM")
