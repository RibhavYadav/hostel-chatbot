from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import AdminStudent, Student
from app.models.schemas import LoginRequest, RegisterRequest, StudentResponse, TokenResponse
from app.services.auth_service import create_access_token, hash_password, verify_password

router = APIRouter()


@router.post("/register", response_model=dict)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new student account.
    """

    # Validate registration number with the admin dataset
    admin_record = (
        db.query(AdminStudent)
        .filter(AdminStudent.registration_number == request.registrationNumber)
        .first()
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
    existing = (
        db.query(Student).filter(Student.registration_number == request.registrationNumber).first()
    )

    if existing:
        raise HTTPException(
            status_code=409, detail="An account for this registration number already exists."
        )

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
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a student and return a JWT token.
    """

    # Find student account
    student = (
        db.query(Student).filter(Student.registration_number == request.registrationNumber).first()
    )

    if not student:
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    # Verify email
    if student.email.lower() != request.emailID.lower():
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    # Verify password
    if not verify_password(request.password, student.hashed_password):
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
