"""
Reusable query builders.
"""
from typing import List, Dict, Any
from datetime import datetime

from .firestore import query_collection
from .collections import Collections

async def candidates_by_status(status: str) -> List[Dict[str, Any]]:
    """Get candidates by their current status."""
    return await query_collection(
        Collections.CANDIDATES,
        filters=[("status", "==", status)]
    )

async def candidates_by_job(job_id: str) -> List[Dict[str, Any]]:
    """Get candidates associated with a specific job via applications."""
    # Applications map candidates to jobs
    applications = await query_collection(
        Collections.APPLICATIONS,
        filters=[("jobId", "==", job_id)]
    )
    return applications

async def candidates_by_stage(pipeline_stage: str) -> List[Dict[str, Any]]:
    """Get applications/candidates at a specific pipeline stage."""
    return await query_collection(
        Collections.APPLICATIONS,
        filters=[("stage", "==", pipeline_stage)]
    )

async def recent_activity(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent activity logs."""
    return await query_collection(
        Collections.ACTIVITY_LOGS,
        order_by="-createdAt",
        limit=limit
    )

async def jobs_by_recruiter(recruiter_id: str) -> List[Dict[str, Any]]:
    """Get jobs posted by a specific recruiter."""
    return await query_collection(
        Collections.JOBS,
        filters=[("recruiterId", "==", recruiter_id)]
    )

async def applications_by_candidate(candidate_id: str) -> List[Dict[str, Any]]:
    """Get applications submitted by a specific candidate."""
    return await query_collection(
        Collections.APPLICATIONS,
        filters=[("candidateId", "==", candidate_id)]
    )

async def interviews_scheduled_between(start: datetime, end: datetime) -> List[Dict[str, Any]]:
    """Get interviews scheduled within a time range."""
    return await query_collection(
        Collections.INTERVIEWS,
        filters=[
            ("scheduledAt", ">=", start),
            ("scheduledAt", "<=", end)
        ]
    )
