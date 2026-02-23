from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    student_id: Optional[str] = None

class IntentResult(BaseModel):
    tag: str
    confidence: float

class ChatResponse(BaseModel):
    message: str
    intent: IntentResult
    requires_form: bool

class LeaveRequest(BaseModel):
    student_id: str
    start_date: str
    end_date: str
    reason: str
    status: str = "pending"
