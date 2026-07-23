"""Notifications controller — recruiter notification feed and candidate messaging."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.services.notification_service import NotificationService
from backend.shared.response import success_response, APIResponse

router = APIRouter(tags=["Notifications"])


class SendNotificationRequest(BaseModel):
    candidate_id: str
    subject: str
    body: str
    channel: str = "email"


@router.get("", response_model=APIResponse)
async def list_notifications(unread_only: bool = False, limit: int = 50):
    svc = NotificationService()
    notifications = await svc.list_notifications(unread_only=unread_only, limit=limit)
    return success_response(notifications)


@router.post("/send", response_model=APIResponse)
async def send_notification(req: SendNotificationRequest):
    svc = NotificationService()
    result = await svc.send_notification(
        req.candidate_id, req.subject, req.body, req.channel
    )
    return success_response(result, "Notification sent")


@router.patch("/{id}/read", response_model=APIResponse)
async def mark_read(id: str):
    svc = NotificationService()
    result = await svc.mark_read(id)
    return success_response(result, "Notification marked as read")
