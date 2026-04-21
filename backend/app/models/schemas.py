from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator


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

    @field_validator("password")
    @classmethod
    def password_requirements(cls, value: str) -> str:
        """
        Validates that the password meets minimum security requirements.
        Must be at least 8 characters, contain one uppercase letter,
        and contain one number. Applied before any database operations.
        """
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one number.")
        return value


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


# Admin auth
class AdminRegisterRequest(BaseModel):
    """
    Request body for admin registration.
    email and adminTeam are validated against the AdminData table.
    Both must match an existing record before the account is created.
    """

    emailID: str
    adminTeam: str
    password: str
    confirmPassword: str

    @field_validator("password")
    @classmethod
    def password_requirements(cls, value: str) -> str:
        """
        Validates that the password meets minimum security requirements.
        Must be at least 8 characters, contain one uppercase letter,
        and contain one number. Applied before any database operations.
        """
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one number.")
        return value


class AdminLoginRequest(BaseModel):
    """
    Request body for admin login.
    Returns a JWT token with email and adminTeam claims on success.
    """

    emailID: str
    password: str


class AdminResponse(BaseModel):
    """
    Admin data returned after login or registration.
    Does not include the hashed password.
    """

    emailID: str
    adminTeam: str


class AdminTokenResponse(BaseModel):
    """
    Returned after successful admin login.
    access_token is a JWT signed with the same secret as student tokens.
    admin carries the admin's profile for the frontend session.
    """

    access_token: str
    token_type: str = "bearer"
    admin: AdminResponse


# Password change
class ChangePasswordRequest(BaseModel):
    """
    Request body for password change for both students and admins.
    currentPassword is verified against the stored hash before
    the new password is applied. newPassword and confirmNewPassword
    must match or the request is rejected.
    """

    currentPassword: str
    newPassword: str
    confirmNewPassword: str

    @field_validator("newPassword")
    @classmethod
    def password_requirements(cls, value: str) -> str:
        """
        Validates that the password meets minimum security requirements.
        Must be at least 8 characters, contain one uppercase letter,
        and contain one number. Applied before any database operations.
        """
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one number.")
        return value


# Chat log
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


# Intent management
class IntentModel(BaseModel):
    """
    Used when returning the full intent list to admins.
    Represents a single intent as it exists in intents.json.
    """

    tag: str
    patterns: List[str]
    responses: List[str]


class IntentCreateRequest(BaseModel):
    """
    Request body for adding a new intent.
    All three fields are required, a new intent must have
    at least one pattern and one response to be valid for training.
    """

    tag: str
    patterns: List[str]
    responses: List[str]


class IntentUpdateRequest(BaseModel):
    """
    Request body for updating an existing intent.
    Both fields are optional, the admin may update only patterns,
    only responses, or both in a single request.
    Fields that are None are left unchanged.
    """

    patterns: Optional[List[str]] = None
    responses: Optional[List[str]] = None


# Leave request status
class LeaveStatusUpdate(BaseModel):
    """
    Request body for approving or rejecting a leave request.
    Only status can be changed by an admin after submission.
    Accepted values are 'approved' or 'rejected' only.
    """

    status: str

    @field_validator("status")
    @classmethod
    def status_validation(cls, value):
        """Ensures status can only be set to approved or rejected."""
        if value not in ("approved", "rejected"):
            raise ValueError("Status must be 'approved' or 'rejected'.")
        return value
