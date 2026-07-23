"""Job model."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any

class Job(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: Optional[str] = None
    title: str = "Job Title"
    department: str = "General"
    location: str = "Remote"
    type: str = "Full-time"
    description: Optional[str] = None
    requirements: Dict[str, Any] = Field(default_factory=dict)
    status: str = "active"
    created_at: Optional[Any] = Field(default=None, alias="createdAt")
    updated_at: Optional[Any] = Field(default=None, alias="updatedAt")
