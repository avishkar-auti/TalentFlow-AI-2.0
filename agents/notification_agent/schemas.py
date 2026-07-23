from pydantic import BaseModel

class NotificationResponse(BaseModel):
    success: bool
    message: str
