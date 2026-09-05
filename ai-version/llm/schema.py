from pydantic import BaseModel
from typing import Optional

class TaskTriageRequest(BaseModel):
    title: str
    context: Optional[str] = None

class TaskTriageResponse(BaseModel):
    category: str
    urgency: str
    estimated_effort: str
    confidence: float
    reason: str
