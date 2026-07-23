from fastapi import APIRouter
from .models import NotificationPayload
from .schemas import NotificationResponse
from .service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])
service = NotificationService()

@router.post("/", response_model=NotificationResponse)
def send_notification(payload: NotificationPayload):
    return service.send(payload)
