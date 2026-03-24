from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


# Student auth
class RegisterRequest(BaseModel):
    """
    Request body for student registration.
    registrationNumber and emailID are validated with the AdminStudent
    table before the account is created. Both must match an existing record.
    confirmPassword is checked against password in the endpoint. If they
    do not match the request is rejected before any database write occurs.
    """

    registrationNumber: int
    emailID: str
    password: str
    confirmPassword: str


class LoginRequest(BaseModel):
    """
    Request body for student login.
    registrationNumber is the primary lookup key.
    emailID is verified as a secondary check against the stored record.
    """

    registrationNumber: int
    emailID: str
    password: str


class StudentResponse(BaseModel):
    """
    Student profile data returned after login or registration.
    Carried inside TokenResponse so the frontend can populate
    the current user session without a second request.
    Does not include hashed password or internal database id.
    """

    registrationNumber: int
    name: str
    emailID: str
    department: str


class TokenResponse(BaseModel):
    """
    Returned after successful student login.
    access_token is a signed JWT containing the student's
    registrationNumber as the subject, valid for 24 hours.
    student carries the full profile for the frontend AuthState.
    """

    access_token: str
    token_type: str = "bearer"
    student: StudentResponse


# Chat
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


# Leave request
class LeaveRequestCreate(BaseModel):
    """
    Request body for submitting a new leave request.
    departureDate must be before returnDate.
    """

    departureDate: date
    returnDate: date
    reason: str


class LeaveRequestResponse(BaseModel):
    """
    A leave request record returned to the student or admin.
    status reflects the current state: 'pending', 'approved', or 'rejected'.
    submittedAt is the UTC timestamp of when the request was created.
    from_attributes=True allows this schema to be built directly
    from a SQLAlchemy ORM row returned by a database query.
    """

    id: int
    studentId: int
    departureDate: date
    returnDate: date
    reason: str
    status: str
    submittedAt: datetime

    class Config:
        from_attributes = True
