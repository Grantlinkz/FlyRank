from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TaskCategory(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    INFRASTRUCTURE = "infrastructure"
    DOCUMENTATION = "documentation"
    OTHER = "other"


class TaskUrgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskEffort(str, Enum):
    QUICK_WIN = "quick_win"
    MEDIUM_TASK = "medium_task"
    DEEP_WORK = "deep_work"


class TaskTriageRequest(BaseModel):
    title: str = Field(..., description="Short task title (1-200 characters)", example="Fix database connection pool exhaustion")
    context: Optional[str] = Field(None, description="Optional extra task context (max 1000 characters)", example="Under high concurrent traffic, connection pool drops requests.")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("title cannot be empty or whitespace only")
        if len(stripped) > 200:
            raise ValueError("title cannot exceed 200 characters")
        return stripped

    @field_validator("context")
    @classmethod
    def validate_context(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if len(stripped) > 1000:
                raise ValueError("context cannot exceed 1000 characters")
            return stripped or None
        return None


class TaskTriageResponse(BaseModel):
    category: TaskCategory = Field(..., description="Classified category from closed enum list")
    urgency: TaskUrgency = Field(..., description="Assessed urgency level from closed enum list")
    estimated_effort: TaskEffort = Field(..., description="Estimated effort level from closed enum list")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    reason: str = Field(..., description="Concise explanation for the triage decision")


class LLMCallTelemetry(BaseModel):
    prompt_version: str
    model: str
    input_tokens: Optional[int] = 0
    output_tokens: Optional[int] = 0
    duration_ms: float
    repaired: bool = False
