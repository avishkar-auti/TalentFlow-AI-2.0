from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Any

class Skill(BaseModel):
    name: str
    category: Optional[str] = None
    level: Optional[str] = None

class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None

class Experience(BaseModel):
    company: str = ""
    title: str = ""
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: List[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, data: Any) -> Any:
        # Tolerate alternate keys some parsers/LLMs emit (role→title, single-string description).
        if isinstance(data, dict):
            if "title" not in data and "role" in data:
                data["title"] = data.get("role")
            desc = data.get("description")
            if isinstance(desc, str):
                data["description"] = [desc]
        return data

    @field_validator("description", mode="before")
    @classmethod
    def _desc_list(cls, v: Any) -> Any:
        if isinstance(v, str):
            return [v]
        return v

class Project(BaseModel):
    name: str = ""
    description: str = ""
    technologies: List[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, data: Any) -> Any:
        # Tolerate title→name and tech→technologies key drift.
        if isinstance(data, dict):
            if "name" not in data and "title" in data:
                data["name"] = data.get("title")
            if "technologies" not in data and "tech" in data:
                data["technologies"] = data.get("tech")
        return data

class Certification(BaseModel):
    name: str
    issuer: str
    date: Optional[str] = None

class ResumeAnalysis(BaseModel):
    skills: List[Skill] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    companies: List[str] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    summary: str = ""

    @field_validator("experience", mode="before")
    @classmethod
    def _experience_to_list(cls, v: Any) -> Any:
        # A summary string like "2+ Years" isn't structured experience — drop it to an
        # empty list rather than hard-failing validation for the entire resume analysis.
        if isinstance(v, str):
            return []
        return v

class ResumeScore(BaseModel):
    # Scores are percentages produced by the ATS scanner (e.g. 82.7), so they must be
    # floats — an int field rejects any value with a fractional part in Pydantic v2.
    ats_score: float
    resume_score: float
    missing_keywords: List[str] = Field(default_factory=list)

class ResumeAnalysisResult(BaseModel):
    analysis: ResumeAnalysis
    score: ResumeScore
