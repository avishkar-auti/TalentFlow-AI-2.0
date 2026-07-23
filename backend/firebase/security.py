"""
Security rules validation.
"""
import logging
from typing import Dict, Any

from .authentication import get_user

logger = logging.getLogger("firebase")


def get_user_claims(uid: str) -> Dict[str, Any]:
    """Helper to retrieve custom claims for a user."""
    try:
        user = get_user(uid)
        return user.custom_claims or {}
    except Exception as e:
        logger.error(f"Could not fetch claims for uid {uid}: {e}")
        return {}


def check_admin_access(uid: str) -> bool:
    """Check if the user has an admin role."""
    claims = get_user_claims(uid)
    return claims.get("role") == "admin"


def check_recruiter_access(uid: str, resource_id: str = None) -> bool:
    """
    Check if the user has recruiter access.
    Optionally, verify access to a specific resource.
    """
    claims = get_user_claims(uid)
    return claims.get("role") in ["admin", "recruiter"]


def check_candidate_access(uid: str, candidate_id: str) -> bool:
    """
    Check if the user has access to a candidate profile.
    Candidates can access their own profile. Admins and recruiters can also access.
    """
    claims = get_user_claims(uid)
    role = claims.get("role")
    
    if role in ["admin", "recruiter"]:
        return True
        
    if role == "candidate" and uid == candidate_id:
        return True
        
    return False
