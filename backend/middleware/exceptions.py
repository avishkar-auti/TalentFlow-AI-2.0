from fastapi import Request
from fastapi.responses import JSONResponse
from backend.logger import get_logger
from backend.middleware.request_id import request_id_var

error_logger = get_logger("errors")

class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(APIError):
    def __init__(self, message: str):
        super().__init__(message, 422)

class NotFoundError(APIError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)

class UnauthorizedError(APIError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)

class ForbiddenError(APIError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403)

class RateLimitError(APIError):
    def __init__(self, message: str = "Too many requests"):
        super().__init__(message, 429)

def register_exception_handlers(app):
    """
    Registers global exception handlers for the FastAPI app.
    """
    
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        req_id = request_id_var.get()
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "request_id": req_id
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        req_id = request_id_var.get()
        error_logger.error(f"Unhandled server error: {str(exc)}", exc_info=True, extra={"request_id": req_id})
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "request_id": req_id
            }
        )
