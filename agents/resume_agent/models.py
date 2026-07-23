from pydantic import BaseModel, Field
from typing import List, Optional

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
    company: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: List[str] = Field(default_factory=list)

class Project(BaseModel):
    name: str
    description: str
    technologies: List[str] = Field(default_factory=list)

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

class ResumeScore(BaseModel):
    ats_score: int
    resume_score: int
    missing_keywords: List[str] = Field(default_factory=list)

class ResumeAnalysisResult(BaseModel):
    analysis: ResumeAnalysis
    score: ResumeScore
