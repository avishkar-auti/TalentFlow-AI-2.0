"""
Firebase initialization.
"""
import logging
import os
from typing import Optional

import firebase_admin
from firebase_admin import credentials, App

logger = logging.getLogger("firebase")

_firebase_app: Optional[App] = None


def initialize_firebase(cred_path: Optional[str] = None, storage_bucket: Optional[str] = None) -> Optional[App]:
    """
    Initialize Firebase Admin SDK using credentials path.
    """
    global _firebase_app
    
    if _firebase_app is not None:
        logger.info("Firebase already initialized.")
        return _firebase_app
        
    try:
        from backend.config import settings
        cred_path = cred_path or getattr(settings, "firebase_credentials_path", None) or os.environ.get("FIREBASE_CREDENTIALS_PATH") or "./firebase-credentials.json"
        
        # Convert to absolute path relative to current working dir or project root
        if cred_path and not os.path.isabs(cred_path):
            cred_path = os.path.abspath(cred_path)

        options = {}
        bucket = storage_bucket or getattr(settings, "firebase_storage_bucket", None) or os.environ.get("FIREBASE_STORAGE_BUCKET")
        if bucket:
            options["storageBucket"] = bucket
            
        if not cred_path or not os.path.exists(cred_path):
            logger.warning(f"Firebase credentials not found at '{cred_path}'. Attempting default initialization.")
            _firebase_app = firebase_admin.initialize_app(options=options if options else None)
        else:
            cred = credentials.Certificate(cred_path)
            _firebase_app = firebase_admin.initialize_app(cred, options=options if options else None)
            logger.info(f"Firebase initialized successfully with credentials at: {cred_path}")
            
        return _firebase_app
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        return None


def get_firebase_app() -> Optional[App]:
    """
    Get the initialized Firebase app.
    Initialize default if not already initialized.
    """
    global _firebase_app
    if _firebase_app is None:
        return initialize_firebase()
    return _firebase_app
