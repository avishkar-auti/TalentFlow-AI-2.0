"""Utility functions for TalentFlow-AI."""
import uuid
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Union

def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())

def utc_now() -> datetime:
    """Get current time in UTC."""
    return datetime.now(timezone.utc)

def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.isoformat()

def calculate_experience_years(start_date: datetime, end_date: datetime = None) -> float:
    """Calculate years of experience between two dates."""
    if not end_date:
        end_date = utc_now()
    delta = end_date - start_date
    return round(delta.days / 365.25, 1)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove unsafe characters."""
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max_length."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def merge_scores(scores: List[float]) -> float:
    """Calculate simple average of scores."""
    if not scores:
        return 0.0
    return sum(scores) / len(scores)

def weighted_average(items: List[Dict[str, Union[float, int]]]) -> float:
    """
    Calculate weighted average.
    items: List of dicts like [{"score": 80, "weight": 0.6}, {"score": 90, "weight": 0.4}]
    """
    total_weight = sum(item.get("weight", 1) for item in items)
    if total_weight == 0:
        return 0.0
    weighted_sum = sum(item.get("score", 0) * item.get("weight", 1) for item in items)
    return weighted_sum / total_weight
