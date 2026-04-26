from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """
    Request body for a chat message.
    message is the raw text typed by the student.
    studentId is optional here for schema compatibility.
    """

    message: str
    studentId: Optional[int] = None


class IntentResult(BaseModel):
    """
    The model's prediction for a given message.
    tag is the intent label with the highest confidence score.
    confidence is a float between 0.0 and 1.0.
    """

    tag: str
    confidence: float


class ChatResponse(BaseModel):
    """
    Response returned to the frontend after a chat message.
    message is the bot's reply text selected from intents.json.
    intent carries the predicted tag and confidence for frontend use.
    requiresForm is True only when the predicted tag is 'leave_request'.
    """

    message: str
    intent: IntentResult
    requiresForm: bool


class ChatLogResponse(BaseModel):
    """
    A single chat log entry returned to admins for review.
    promoted=False means this message is pending review.
    promoted=True means it has already been added as a training pattern.
    """

    id: int
    studentId: int
    message: str
    predictedTag: str
    confidence: float
    botResponse: str
    timestamp: datetime
    promoted: bool

    class Config:
        from_attributes = True
