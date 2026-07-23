import time
import json
from typing import Awaitable, Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from backend.logger import get_logger
from backend.middleware.request_id import request_id_var

api_logger = get_logger("api")

def redact_pii(data: dict) -> dict:
    """Redacts PII fields from a dictionary."""
    if not isinstance(data, dict):
        return data
        
    redacted = {}
    pii_fields = {"password", "email", "ssn", "phone", "token", "authorization"}
    
    for k, v in data.items():
        if k.lower() in pii_fields:
            redacted[k] = "***REDACTED***"
        elif isinstance(v, dict):
            redacted[k] = redact_pii(v)
        elif isinstance(v, list):
            redacted[k] = [redact_pii(item) if isinstance(item, dict) else item for item in v]
        else:
            redacted[k] = v
    return redacted

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request and response details, including duration and redacted body for POST/PUT.
    """
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Don't log health check spam
        if request.url.path in ("/health", "/healthcheck", "/api/health"):
            return await call_next(request)

        start_time = time.time()
        req_id = request_id_var.get()
        
        log_meta = {
            "method": request.method,
            "path": request.url.path,
            "request_id": req_id
        }

        # Safely read request body for POST/PUT/PATCH
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body_bytes = await request.body()
                if body_bytes:
                    try:
                        body_json = json.loads(body_bytes)
                        log_meta["body"] = redact_pii(body_json)
                    except json.JSONDecodeError:
                        log_meta["body"] = "<non-json body>"
                
                # Re-inject the body for downstream consumption
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                request._receive = receive
            except Exception as e:
                log_meta["body_error"] = str(e)

        api_logger.info(f"Incoming request {request.method} {request.url.path}", extra=log_meta)
        
        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_meta["status_code"] = response.status_code
            log_meta["duration_ms"] = duration_ms
            api_logger.info(f"Completed request {request.method} {request.url.path} with status {response.status_code}", extra=log_meta)
            return response
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            log_meta["duration_ms"] = duration_ms
            api_logger.error(f"Failed request {request.method} {request.url.path}", extra=log_meta, exc_info=True)
            raise
