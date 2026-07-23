"""Standardized API response formats."""
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

def get_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

def get_request_id() -> str:
    return str(uuid.uuid4())

class APIResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: str = ""
    error: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = Field(default_factory=get_request_id)
    timestamp: str = Field(default_factory=get_timestamp)

def success_response(data: Any = None, message: str = "Success", request_id: Optional[str] = None) -> APIResponse:
    """Create a standardized success response."""
    return APIResponse(
        success=True,
        data=data,
        message=message,
        request_id=request_id or get_request_id(),
        timestamp=get_timestamp()
    )

def error_response(error: Dict[str, Any], message: str = "Error", request_id: Optional[str] = None) -> APIResponse:
    """Create a standardized error response."""
    return APIResponse(
        success=False,
        error=error,
        message=message,
        request_id=request_id or get_request_id(),
        timestamp=get_timestamp()
    )
