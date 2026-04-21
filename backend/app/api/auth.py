from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import AdminStudent, Student
from app.models.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    StudentResponse,
    TokenResponse,
)
from app.services.auth_service import create_access_token, get_current_student, hash_password, verify_password

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/register", response_model=dict)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new student account. Validates registration number against AdminStudent table,
    the number myst exist in the admin database.
    Validates submitted email matches the record for the registration number.
    Rejects the request if an account for the registration number already exists to prevent
    duplicates.
    Name and department are pulled from the admin record.
    """

    # Validate registration number with the admin dataset
    admin_record = (
        db.query(AdminStudent).filter(AdminStudent.registration_number == request.registrationNumber).first()
    )

    if not admin_record:
        raise HTTPException(
            status_code=403,
            detail="Registration Number not recognised. Please contact your department.",
        )

    # Validate email matches the admin record
    if admin_record.email.lower() != request.emailID.lower():
        raise HTTPException(status_code=403, detail="Email does not match our records.")

    # Check if account already exists
    existing = db.query(Student).filter(Student.registration_number == request.registrationNumber).first()

    if existing:
        raise HTTPException(status_code=409, detail="An account for this registration number already exists.")

    # Validate passwords
    if request.password != request.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    # Create an account for the student
    new_student = Student(
        registration_number=request.registrationNumber,
        name=admin_record.name,
        email=admin_record.email,
        department=admin_record.department,
        hashed_password=hash_password(request.password),
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {"message": "Account created successfully. You can now log in."}


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a student and return a JWT token.
    Verifies email and password for the registration number in use.
    'Invalid credentials' is returned on failed matches.
    Returns a TokenResponse containing the signed JWT token and student profile for the frontend.
    Token is valid for the duration set in JWT_EXPIRE_MINUTES.
    Rate limited to 5 attempts per minute per IP address.
    """

    # Find student account
    student = db.query(Student).filter(Student.registration_number == payload.registrationNumber).first()

    if not student:
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    # Verify email
    if student.email.lower() != payload.emailID.lower():
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    # Verify password
    if not verify_password(payload.password, student.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    # Return token and student info
    token = create_access_token(student.registration_number)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        student=StudentResponse(
            registrationNumber=student.registration_number,
            name=student.name,
            emailID=student.email,
            department=student.department,
        ),
    )


@router.post("/change-password", response_model=dict)
def change_password(
    request: ChangePasswordRequest,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    """
    Changes the password for the authenticated student.
    Current password is verified before applying the change.
    Validates that the new password differs from the current one,
    newPassword and confirmPassword are matched before updating database.
    """

    # Verify current password
    if not verify_password(request.currentPassword, current_student.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")

    # Verify new passwords match
    if request.newPassword != request.confirmNewPassword:
        raise HTTPException(status_code=400, detail="New password does not match.")

    # Verify new password does not match current password
    if verify_password(request.newPassword, current_student.hashed_password):
        raise HTTPException(status_code=400, detail="New password must not match the current password.")

    # Update password
    current_student.hashed_password = hash_password(request.newPassword)
    db.commit()

    return {"message": "Password changed successfully."}
