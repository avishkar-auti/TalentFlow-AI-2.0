import fitz  # PyMuPDF
import re
from typing import List, Dict, Any, Tuple
from .models import ResumeAnalysis

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from a PDF file using PyMuPDF."""
    text = ""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    return text

def clean_extracted_text(text: str) -> str:
    """Normalizes whitespace and cleans up extracted text."""
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def calculate_ats_score(skills: List[str], job_requirements: List[str]) -> Tuple[int, List[str]]:
    """Calculates an ATS score deterministically based on keyword matching."""
    if not job_requirements:
        return 100, []
    
    skills_lower = {s.lower() for s in skills}
    reqs_lower = {r.lower() for r in job_requirements}
    
    matched = reqs_lower.intersection(skills_lower)
    missing = list(reqs_lower - skills_lower)
    
    if not reqs_lower:
        return 100, missing
        
    score = int((len(matched) / len(reqs_lower)) * 100)
    return score, missing

def calculate_resume_quality_score(analysis: ResumeAnalysis) -> int:
    """Calculates a quality score based on resume completeness."""
    score = 0
    if analysis.experience:
        score += 40
    if analysis.education:
        score += 20
    if analysis.skills:
        score += 20
    if analysis.summary:
        score += 10
    if analysis.projects or analysis.certifications:
        score += 10
    
    if analysis.experience and all(len(exp.description) > 0 for exp in analysis.experience):
        score = min(100, score + 10)
        
    return min(100, score)
