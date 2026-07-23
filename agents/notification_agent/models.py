from pydantic import BaseModel
from typing import Dict, Any

class NotificationPayload(BaseModel):
    type: str
    recipient: str
    data: Dict[str, Any]
