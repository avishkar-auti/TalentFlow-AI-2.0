"""
Firebase Storage operations.
"""
import logging
from datetime import timedelta
from typing import List, Union

from firebase_admin import storage
from .firebase import get_firebase_app

logger = logging.getLogger("firebase")


def _get_bucket():
    app = get_firebase_app()
    if not app:
        raise RuntimeError("Firebase app not initialized")
    return storage.bucket(app=app)


def upload_file(bucket_path: str, local_path_or_bytes: Union[str, bytes], content_type: str) -> str:
    """Upload a file to Firebase Storage."""
    try:
        bucket = _get_bucket()
        blob = bucket.blob(bucket_path)
        
        if isinstance(local_path_or_bytes, str):
            blob.upload_from_filename(local_path_or_bytes, content_type=content_type)
        else:
            blob.upload_from_string(local_path_or_bytes, content_type=content_type)
            
        logger.info(f"File uploaded to {bucket_path}")
        
        blob.make_public()
        return blob.public_url
    except Exception as e:
        logger.error(f"Failed to upload file to {bucket_path}: {e}")
        raise


def download_file(bucket_path: str) -> bytes:
    """Download a file from Firebase Storage as bytes."""
    try:
        bucket = _get_bucket()
        blob = bucket.blob(bucket_path)
        content = blob.download_as_bytes()
        logger.info(f"File downloaded from {bucket_path}")
        return content
    except Exception as e:
        logger.error(f"Failed to download file from {bucket_path}: {e}")
        raise


def get_signed_url(bucket_path: str, expiration_minutes: int = 60) -> str:
    """Get a signed URL for temporary access to a file."""
    try:
        bucket = _get_bucket()
        blob = bucket.blob(bucket_path)
        url = blob.generate_signed_url(expiration=timedelta(minutes=expiration_minutes))
        return url
    except Exception as e:
        logger.error(f"Failed to generate signed URL for {bucket_path}: {e}")
        raise


def delete_file(bucket_path: str) -> None:
    """Delete a file from Firebase Storage."""
    try:
        bucket = _get_bucket()
        blob = bucket.blob(bucket_path)
        blob.delete()
        logger.info(f"File deleted at {bucket_path}")
    except Exception as e:
        logger.error(f"Failed to delete file {bucket_path}: {e}")
        raise


def list_files(prefix: str) -> List[str]:
    """List files in a given prefix (directory)."""
    try:
        bucket = _get_bucket()
        blobs = bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]
    except Exception as e:
        logger.error(f"Failed to list files with prefix {prefix}: {e}")
        raise
