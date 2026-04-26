from datetime import date, datetime

from pydantic import BaseModel, field_validator


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
