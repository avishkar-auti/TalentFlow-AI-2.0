import sys
from pathlib import Path

# Ensure project root is in sys.path so 'backend' package imports resolve correctly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import uuid
import time
from fastapi.responses import JSONResponse
from .config import settings
from .logger import api_logger, request_id_var, errors_logger
from backend.firebase.firebase import initialize_firebase


from .controllers import (
    auth_router, candidates_router, jobs_router, interviews_router,
    dashboard_router, reports_router, resume_router, matching_router,
    decision_router, health_router, applications_router, notifications_router,
    recruiters_router, admin_router, analytics_router, internal_router,
    code_sandbox_router,
)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan events for FastAPI app."""
    api_logger.info("Starting up FastAPI application")
    initialize_firebase()
    yield
    api_logger.info("Shutting down FastAPI application")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="TalentFlow-AI API",
        version="1.0.0",
        lifespan=lifespan
    )

    origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip() and origin.strip() != "*"]
    default_origins = [
        "http://localhost:3000", "http://localhost:3001", "http://localhost:5173", "http://localhost:5174",
        "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:5173", "http://127.0.0.1:5174"
    ]
    # Merge configured origins with default local origins
    all_origins = list(set(origins + default_origins))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=all_origins,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    @app.middleware("http")
    async def request_middleware(request: Request, call_next):
        """Middleware to handle request ID, logging, and metrics."""
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        
        start_time = time.time()
        api_logger.info("Request started", method=request.method, url=str(request.url))
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            api_logger.info(
                "Request completed", 
                status_code=response.status_code, 
                process_time=process_time
            )
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as exc:
            process_time = time.time() - start_time
            errors_logger.error(
                "Unhandled exception", 
                exc_info=exc,
                method=request.method,
                url=str(request.url),
                process_time=process_time
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"}
            )

    PREFIX = "/api/v1"

    # ── Core pipeline routes ──────────────────────────────────────────────────
    app.include_router(auth_router,         prefix=f"{PREFIX}/auth")
    app.include_router(candidates_router,   prefix=f"{PREFIX}/candidates")
    app.include_router(jobs_router,         prefix=f"{PREFIX}/jobs")
    app.include_router(interviews_router,   prefix=f"{PREFIX}/interviews")
    app.include_router(dashboard_router,    prefix=f"{PREFIX}/dashboard")
    app.include_router(reports_router,      prefix=f"{PREFIX}/reports")
    app.include_router(applications_router, prefix=f"{PREFIX}/applications")
    app.include_router(notifications_router, prefix=f"{PREFIX}/notifications")
    app.include_router(recruiters_router,   prefix=f"{PREFIX}/recruiters")

    # ── Admin, analytics, internal (flat prefixes per spec) ──────────────────
    app.include_router(admin_router,        prefix=PREFIX)   # /api/v1/admin/...
    app.include_router(analytics_router,    prefix=PREFIX)   # /api/v1/analytics/...
    app.include_router(internal_router,     prefix=PREFIX)   # /api/v1/internal/...
    app.include_router(code_sandbox_router, prefix=PREFIX)   # /api/v1/internal/execute-code

    # ── Sub-controllers with self-contained router prefixes ─────────────────
    app.include_router(resume_router,       prefix=PREFIX)   # /api/v1/resume/...
    app.include_router(matching_router,     prefix=PREFIX)   # /api/v1/matching/...
    app.include_router(decision_router,     prefix=PREFIX)   # /api/v1/decision/...
    app.include_router(health_router,       prefix=PREFIX)   # /api/v1/health

    # ── Root WebSocket Aliases (supports client connections to ws://localhost:8000/ws/interview/...) ──
    from .controllers.interviews import ws_interview_session, ws_vision_proctoring
    app.websocket("/ws/interview/{interview_id}")(ws_interview_session)
    app.websocket("/ws/interview/{interview_id}/vision")(ws_vision_proctoring)
    app.websocket(f"{PREFIX}/ws/interview/{{interview_id}}")(ws_interview_session)
    app.websocket(f"{PREFIX}/ws/interview/{{interview_id}}/vision")(ws_vision_proctoring)
    from .controllers.interviews import ws_recruiter_chat
    app.websocket('/ws/recruiter-chat/{interview_id}')(ws_recruiter_chat)
    app.websocket(f'{PREFIX}/ws/recruiter-chat/{{interview_id}}')(ws_recruiter_chat)

    return app


# Module-level instance — supports both `python -m backend.main` and `uvicorn backend.app:app`
app = create_app()
