from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import LeaveRequest, Student
from app.models.schemas import LeaveRequestCreate, LeaveRequestResponse
from app.services.auth_service import get_current_student

router = APIRouter()


@router.post("/submit", response_model=LeaveRequestResponse)
def submit_leave(
    request: LeaveRequestCreate,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Submit a leave request for the authenticated student.
    Validates that departure date is before return date.
    """

    if request.departureDate >= request.returnDate:
        raise HTTPException(status_code=400, detail="Departure date is before return date.")

    leave = LeaveRequest(
        student_id=current_student.id,
        departure_date=request.departureDate,
        return_date=request.returnDate,
        reason=request.reason,
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)

    return LeaveRequestResponse(
        id=leave.id,
        studentId=leave.student_id,
        departureDate=leave.departure_date,
        returnDate=leave.return_date,
        reason=leave.reason,
        status=leave.status,
        submittedAt=leave.submitted_at,
    )


@router.get("/status", response_model=list[LeaveRequestResponse])
def get_leave_status(current_student: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    """
    Returns all leave requests for the authenticated student. Most recent one is returned first.
    """

    requests = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.student_id == current_student.id)
        .order_by(LeaveRequest.submitted_at.desc())
        .all()
    )

    return [
        LeaveRequestResponse(
            id=r.id,
            studentId=r.student_id,
            departureDate=r.departure_date,
            returnDate=r.return_date,
            reason=r.reason,
            status=r.status,
            submittedAt=r.submitted_at,
        )
        for r in requests
    ]


@router.get("/all", response_model=list[LeaveRequestResponse])
def get_all_leave_requests(
    current_student: Student = Depends(get_current_student), db: Session = Depends(get_db)
):
    """
    Returns all leave requests across all students.
    """
    requests = db.query(LeaveRequest).order_by(LeaveRequest.submitted_at.desc()).all()

    return [
        LeaveRequestResponse(
            id=r.id,
            studentId=r.student_id,
            departureDate=r.departure_date,
            returnDate=r.return_date,
            reason=r.reason,
            status=r.status,
            submittedAt=r.submitted_at,
        )
        for r in requests
    ]
