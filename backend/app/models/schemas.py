from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


# Auth schemas
class RegisterRequest(BaseModel):
    registrationNumber: int
    emailID: str
    password: str
    confirmPassword: str


class LoginRequest(BaseModel):
    registrationNumber: int
    emailID: str
    password: str


class StudentResponse(BaseModel):
    registrationNumber: int
    name: str
    emailID: str
    department: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    student: StudentResponse


# Chat schemas
class ChatRequest(BaseModel):
    message: str
    studentId: Optional[int] = None


class IntentResult(BaseModel):
    tag: str
    confidence: float


class ChatResponse(BaseModel):
    message: str
    intent: IntentResult
    requiresForm: bool


# Exit
class ExitRequestCreate(BaseModel):
    departureDate: date
    returnDate: date
    reason: str


class ExitRequestResponse(BaseModel):
    id: int
    studentId: int
    departureDate: date
    returnDate: date
    reason: str
    status: str
    submittedAt: datetime

    class Config:
        from_attributes = True
