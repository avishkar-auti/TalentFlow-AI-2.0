"""
Firebase layer exports.
"""

from .firebase import get_firebase_app, initialize_firebase
from .firestore import get_firestore_client
from .storage import upload_file, download_file, get_signed_url, delete_file, list_files
from .authentication import verify_token, create_user, get_user, set_custom_claims, delete_user
from .security import check_recruiter_access, check_admin_access, check_candidate_access
from .collections import Collections
from .queries import (
    candidates_by_status,
    candidates_by_job,
    candidates_by_stage,
    recent_activity,
    jobs_by_recruiter,
    applications_by_candidate,
    interviews_scheduled_between
)

__all__ = [
    "get_firebase_app",
    "initialize_firebase",
    "get_firestore_client",
    "upload_file",
    "download_file",
    "get_signed_url",
    "delete_file",
    "list_files",
    "verify_token",
    "create_user",
    "get_user",
    "set_custom_claims",
    "delete_user",
    "check_recruiter_access",
    "check_admin_access",
    "check_candidate_access",
    "Collections",
    "candidates_by_status",
    "candidates_by_job",
    "candidates_by_stage",
    "recent_activity",
    "jobs_by_recruiter",
    "applications_by_candidate",
    "interviews_scheduled_between"
]
