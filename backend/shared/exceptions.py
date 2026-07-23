"""Custom exceptions for TalentFlow-AI."""
from typing import Optional, Any, Dict

class TalentFlowError(Exception):
    """Base exception for all TalentFlow-AI errors."""
    def __init__(self, message: str, status_code: int = 500, error_code: str = "INTERNAL_ERROR", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail or {}

class NotFoundError(TalentFlowError):
    def __init__(self, message: str = "Resource not found", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, error_code="NOT_FOUND", detail=detail)

class ValidationError(TalentFlowError):
    def __init__(self, message: str = "Validation error", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR", detail=detail)

class UnauthorizedError(TalentFlowError):
    def __init__(self, message: str = "Unauthorized access", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, error_code="UNAUTHORIZED", detail=detail)

class ForbiddenError(TalentFlowError):
    def __init__(self, message: str = "Forbidden access", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, error_code="FORBIDDEN", detail=detail)

class AgentError(TalentFlowError):
    def __init__(self, message: str = "Agent processing error", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, error_code="AGENT_ERROR", detail=detail)

class LLMError(TalentFlowError):
    def __init__(self, message: str = "LLM service error", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=502, error_code="LLM_ERROR", detail=detail)

class FirestoreError(TalentFlowError):
    def __init__(self, message: str = "Database operation failed", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, error_code="FIRESTORE_ERROR", detail=detail)

class StorageError(TalentFlowError):
    def __init__(self, message: str = "Storage operation failed", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, error_code="STORAGE_ERROR", detail=detail)

class RateLimitError(TalentFlowError):
    def __init__(self, message: str = "Rate limit exceeded", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=429, error_code="RATE_LIMIT", detail=detail)
