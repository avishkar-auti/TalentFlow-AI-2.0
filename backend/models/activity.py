from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any

class ActivityLog(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: Optional[str] = None
    agent_name: Optional[str] = Field(default="System", alias="agentName")
    action: str = "activity"
    details: Optional[Any] = None
    candidate_id: Optional[str] = Field(default=None, alias="candidateId")
    user_id: Optional[str] = Field(default=None, alias="userId")
    timestamp: Optional[Any] = None
