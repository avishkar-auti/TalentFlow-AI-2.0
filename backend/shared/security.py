"""Security utilities for TalentFlow-AI."""
import hashlib
from typing import Dict, Any, List
import re

def redact_pii(data: Dict[str, Any], fields: List[str] = None) -> Dict[str, Any]:
    """
    Replace sensitive fields with [REDACTED].
    Default fields: email, phone, address, ssn.
    """
    if fields is None:
        fields = ["email", "phone", "address", "ssn", "social_security"]
    
    redacted_data = data.copy()
    for key, value in redacted_data.items():
        if isinstance(value, dict):
            redacted_data[key] = redact_pii(value, fields)
        elif isinstance(value, list):
            redacted_data[key] = [
                redact_pii(item, fields) if isinstance(item, dict) else item
                for item in value
            ]
        elif any(f.lower() in key.lower() for f in fields) and value:
            redacted_data[key] = "[REDACTED]"
            
    return redacted_data

def sanitize_input(text: str) -> str:
    """Basic sanitization to prevent injection attacks."""
    if not isinstance(text, str):
        return text
    # Remove null bytes
    text = text.replace('\x00', '')
    # Basic HTML escaping could be added here if needed for specific text
    return text

def hash_identifier(value: str) -> str:
    """Hash a value (like email) for deduplication without storing the raw value."""
    if not value:
        return ""
    return hashlib.sha256(value.lower().strip().encode('utf-8')).hexdigest()
