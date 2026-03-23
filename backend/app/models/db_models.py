from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


# AdminStudent format will be changed if the format of the CSV is different.
class AdminStudent(Base):
    """
    Preloaded by the admin, read-only during runtime.
    Validates registration number and email at registration.
    """

    __tablename__ = "admin_students"

    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    department = Column(String, nullable=False)


class Student(Base):
    """
    Created when a student registers.
    Stores credentials and links to leave requests.
    """

    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    department = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    leave_requests = relationship("LeaveRequest", back_populates="student")


class LeaveRequest(Base):
    """
    Created when a student submits a leave request.
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
