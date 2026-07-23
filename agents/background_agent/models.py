from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class CheckStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    INCONCLUSIVE = "inconclusive"

class CheckSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class BackgroundCheck(BaseModel):
    check_name: str = Field(..., description="The name of the check performed")
    status: CheckStatus = Field(..., description="The outcome of the check")
    detail: str = Field(..., description="Detailed explanation of the result")
    severity: CheckSeverity = Field(..., description="Severity level if the check did not pass")

class BackgroundCheckResult(BaseModel):
    overall_score: float = Field(..., description="Score from 0 to 100")
    checks: List[BackgroundCheck] = Field(default_factory=list, description="List of individual checks")
    flags: List[str] = Field(default_factory=list, description="Specific flags raised during background check")
    concerns: List[str] = Field(default_factory=list, description="Concerns to be reviewed by a human")
    is_clear: bool = Field(..., description="Whether the background check is completely clear")
