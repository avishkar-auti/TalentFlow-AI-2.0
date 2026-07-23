from .agent import NotificationAgent
from .models import NotificationPayload
from .schemas import NotificationResponse

class NotificationService:
    def __init__(self):
        self.agent = NotificationAgent()
        
    def send(self, payload: NotificationPayload) -> NotificationResponse:
        self.agent.send_notification(payload.type, payload.recipient, payload.data)
        return NotificationResponse(success=True, message="Notification dispatched")
