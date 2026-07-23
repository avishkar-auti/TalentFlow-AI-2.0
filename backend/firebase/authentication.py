"""
Firebase Authentication operations.
"""
import logging
from typing import Dict, Any, Optional

from firebase_admin import auth
from .firebase import get_firebase_app

logger = logging.getLogger("firebase")


def verify_token(id_token: str) -> Dict[str, Any]:
    """Verify a Firebase ID token and return its decoded payload."""
    try:
        app = get_firebase_app()
        if not app:
            raise RuntimeError("Firebase app not initialized")
        decoded_token = auth.verify_id_token(id_token, app=app)
        
        uid = decoded_token.get('uid')
        email = decoded_token.get('email')
        
        return {
            "uid": uid,
            "email": email,
            "claims": decoded_token
        }
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise


def create_user(email: str, password: str, display_name: Optional[str] = None) -> auth.UserRecord:
    """Create a new Firebase Auth user."""
    try:
        app = get_firebase_app()
        if not app:
            raise RuntimeError("Firebase app not initialized")
        kwargs = {
            "email": email,
            "password": password
        }
        if display_name:
            kwargs["display_name"] = display_name
            
        user = auth.create_user(app=app, **kwargs)
        logger.info(f"Successfully created new user: {user.uid}")
        return user
    except Exception as e:
        logger.error(f"Failed to create user {email}: {e}")
        raise


def get_user(uid: str) -> auth.UserRecord:
    """Retrieve an existing user by UID."""
    try:
        app = get_firebase_app()
        if not app:
            raise RuntimeError("Firebase app not initialized")
        user = auth.get_user(uid, app=app)
        return user
    except Exception as e:
        logger.error(f"Failed to get user {uid}: {e}")
        raise


def set_custom_claims(uid: str, claims: Dict[str, Any]) -> None:
    """Set custom claims on a user (e.g. for roles like admin, recruiter, candidate)."""
    try:
        app = get_firebase_app()
        if not app:
            raise RuntimeError("Firebase app not initialized")
        auth.set_custom_user_claims(uid, claims, app=app)
        logger.info(f"Custom claims {claims} set for user {uid}")
    except Exception as e:
        logger.error(f"Failed to set custom claims for {uid}: {e}")
        raise


def delete_user(uid: str) -> None:
    """Delete a user."""
    try:
        app = get_firebase_app()
        if not app:
            raise RuntimeError("Firebase app not initialized")
        auth.delete_user(uid, app=app)
        logger.info(f"Successfully deleted user: {uid}")
    except Exception as e:
        logger.error(f"Failed to delete user {uid}: {e}")
        raise
