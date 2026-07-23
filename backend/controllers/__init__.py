"""Controllers package — exports all routers for registration in app.py."""
from .auth import router as auth_router
from .candidates import router as candidates_router
from .jobs import router as jobs_router
from .interviews import router as interviews_router
from .dashboard import router as dashboard_router
from .reports import router as reports_router
from .resume_controller import router as resume_router
from .matching_controller import router as matching_router
from .decision_controller import router as decision_router
from .health_controller import router as health_router
from .applications import router as applications_router
from .notifications import router as notifications_router
from .recruiters import router as recruiters_router
from .admin import router as admin_router
from .analytics import router as analytics_router
from .internal import router as internal_router

__all__ = [
    "auth_router",
    "candidates_router",
    "jobs_router",
    "interviews_router",
    "dashboard_router",
    "reports_router",
    "resume_router",
    "matching_router",
    "decision_router",
    "health_router",
    "applications_router",
    "notifications_router",
    "recruiters_router",
    "admin_router",
    "analytics_router",
    "internal_router",
]
