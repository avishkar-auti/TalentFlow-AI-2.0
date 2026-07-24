"""Job model — enhanced with full fields for TalentFlow-AI-2.0."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any


class JobRequirements(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    skills: List[str] = Field(default_factory=list)
    experience_years: Optional[int] = Field(default=None, alias="experienceYears")
    experience: Optional[str] = None
    education: Optional[str] = None
    nice_to_have: List[str] = Field(default_factory=list, alias="niceToHave")


class Job(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: Optional[str] = None
    title: str = "Job Title"
    department: str = "General"
    location: str = "Remote"
    type: str = "Full-time"
    description: Optional[str] = None
    requirements: Any = Field(default_factory=dict)
    required_skills: List[str] = Field(default_factory=list, alias="requiredSkills")
    experience_level: Optional[str] = Field(default="Mid", alias="experienceLevel")
    salary_range: Optional[str] = Field(default=None, alias="salaryRange")
    status: str = "active"
    application_count: int = Field(default=0, alias="applicationCount")
    posted_by: Optional[str] = Field(default=None, alias="postedBy")
    created_at: Optional[Any] = Field(default=None, alias="createdAt")
    updated_at: Optional[Any] = Field(default=None, alias="updatedAt")
