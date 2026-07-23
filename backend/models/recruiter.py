"""Recruiter model."""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from ..shared.helpers import utc_now, generate_id

class Recruiter(BaseModel):
    id: str = Field(default_factory=generate_id)
    name: str
    email: EmailStr
    company: str
    role: str
    active_jobs: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
