"""Validators for TalentFlow-AI."""
import re
from typing import Optional
import os
from .constants import MAX_RESUME_SIZE_MB, SUPPORTED_RESUME_FORMATS, PIPELINE_STAGES
from .exceptions import ValidationError

def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError(f"Invalid email format: {email}")
    return True

def validate_phone(phone: str) -> bool:
    """Validate phone number format. Allows basic international formats."""
    pattern = r'^\+?1?\d{9,15}$'
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
    if not re.match(pattern, cleaned_phone):
        raise ValidationError(f"Invalid phone format: {phone}")
    return True

def validate_resume_file(filename: str, size_bytes: int) -> bool:
    """Validate resume file type and size."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SUPPORTED_RESUME_FORMATS:
        raise ValidationError(f"Unsupported file format: {ext}. Supported: {SUPPORTED_RESUME_FORMATS}")
    
    size_mb = size_bytes / (1024 * 1024)
    if size_mb > MAX_RESUME_SIZE_MB:
        raise ValidationError(f"File size {size_mb:.1f}MB exceeds limit of {MAX_RESUME_SIZE_MB}MB")
    return True

def validate_pipeline_transition(current_stage: str, next_stage: str) -> bool:
    """Validate if transition between pipeline stages is valid."""
    if current_stage not in PIPELINE_STAGES:
        raise ValidationError(f"Invalid current stage: {current_stage}")
    if next_stage not in PIPELINE_STAGES:
        raise ValidationError(f"Invalid next stage: {next_stage}")
    
    current_idx = PIPELINE_STAGES.index(current_stage)
    next_idx = PIPELINE_STAGES.index(next_stage)
    
    # Can always move to terminal states
    if next_stage in ["hired", "rejected"]:
        return True
    
    # Normally move forward, but can also move backward if needed
    return True

def validate_score(score: float) -> bool:
    """Validate a score is within 0-100 range."""
    if not (0 <= score <= 100):
        raise ValidationError(f"Score {score} must be between 0 and 100")
    return True
