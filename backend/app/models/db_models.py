from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class AdminStudent(Base):
    """
    Loaded from student_data.csv on the first startup. Read-only during runtime.
    Used by the registration endpoint to validate that a student's registration number
    and email exist in the admin dataset before creating an account.
    Will be updated when the actual student dataset CSV is provided.
    """

    __tablename__ = "admin_students"

    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    department = Column(String, nullable=False)


class Student(Base):
    """
    Created when a student completes registration.
    Stores credentials and links to leave requests and chat logs.
    Registration number is the primary identifier used in JWT tokens.
    """

    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    department = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    leave_requests = relationship("LeaveRequest", back_populates="student")
    chat_logs = relationship("ChatLog", back_populates="student")


class LeaveRequest(Base):
    """
    Created when a student submits a leave request.
    Status starts as 'pending' and is updated by a warden or CSO admin.
    reviewed_at is null until an admin acts on the request.
    """

    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    departure_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, default="pending")
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="leave_requests")


class AdminData(Base):
    """
    Loaded from admin_data.csv on first startup. Read-only during runtime.
    Used by the admin registration endpoint to validate that the email and
    admin_team combination exists before creating an Admin account.
    """

    __tablename__ = "admin_data"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    admin_team = Column(String, nullable=False)


class Admin(Base):
    """
    Created when an admin completes registration.
    admin_team determines permission level:
        'cso'     - full access to all endpoints
        'warden'  - leave request management only
        'it'      - intent management, model retraining, chat log review
    Email is the primary identifier used in admin JWT tokens.
    """

    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    admin_team = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ChatLog(Base):
    """
    Created on every student's chat message.
    Stores the student's message, the model's predicted intent, confidence,
    and the response that was returned.
    promoted=False means the message is available for admin review.
    promoted=True means an admin has already added this message for training
    so it will not appear in the review queue again.
    """

    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    message = Column(String, nullable=False)
    predicted_tag = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    bot_response = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    promoted = Column(Boolean, default=False, nullable=False)

    student = relationship("Student", back_populates="chat_logs")
