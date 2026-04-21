from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Admin, AdminData
from app.models.schemas import (
    AdminLoginRequest,
    AdminRegisterRequest,
    AdminResponse,
    AdminTokenResponse,
    ChangePasswordRequest,
)
from app.services.auth_service import (
    create_admin_token,
    get_current_admin,
    hash_password,
    verify_password,
)

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/register", response_model=dict)
def admin_register(request: AdminRegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new admin account.
    Validates the submitted email against the AdminData table, the email must exist in
    the preloaded admin dataset.
    Validates that the submitted adminTeam matches the record for that email in the AdminData table.
    Rejects the request if an account already exists.
    Validates that password and confirmPassword match before writing.
    """

    # Validate email against admin dataset
    admin_record = db.query(AdminData).filter(AdminData.email == request.emailID.lower()).first()

    if not admin_record:
        raise HTTPException(status_code=403, detail="Email not recognised. Contact the system administrator.")

    # Validate admin team matches the record
    if admin_record.admin_team != request.adminTeam:
        raise HTTPException(status_code=403, detail="Admin team does not match our records for this email.")

    # Check if account already exists
    existing = db.query(Admin).filter(Admin.email == request.emailID.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="An account for this email already exists.")

    # Validate passwords match
    if request.password != request.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    # Create admin account
    new_admin = Admin(
        email=request.emailID.lower(),
        admin_team=admin_record.admin_team,
        hashed_password=hash_password(request.password),
    )
    db.add(new_admin)
    db.commit()

    return {"message": "Admin account created successfully. You can now log in."}


@router.post("/login", response_model=AdminTokenResponse)
def admin_login(request: Request, payload: AdminLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates an admin and returns a signed JWT token.
    Looks up the admin by email and verifies the password.
    Both failure cases return the same message to avoid leaking which field was incorrect.
    On success returns an AdminTokenResponse containing the signed JWT with email and team claims,
    and the admin profile.
    """

    # Find admin account
    admin = db.query(Admin).filter(Admin.email == payload.emailID.lower()).first()
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    # Verify password
    if not verify_password(payload.password, admin.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    # Return token and admin info
    token = create_admin_token(admin.email, admin.admin_team)

    return AdminTokenResponse(
        access_token=token,
        token_type="bearer",
        admin=AdminResponse(
            emailID=admin.email,
            adminTeam=admin.admin_team,
        ),
    )


@router.post("/change-password", response_model=dict)
def admin_change_password(
    request: ChangePasswordRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Changes the password for the authenticated admin.
    Current password is verified before applying the change.
    Validates that the new password differs from the current one and that
    newPassword and confirmNewPassword match before updating.
    """

    # Verify current password
    if not verify_password(request.currentPassword, current_admin.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")

    # Verify new passwords match
    if request.newPassword != request.confirmNewPassword:
        raise HTTPException(status_code=400, detail="New passwords do not match.")

    # Verify new password is different from current
    if verify_password(request.newPassword, current_admin.hashed_password):
        raise HTTPException(status_code=400, detail="New password must be different from current password.")

    # Update password
    current_admin.hashed_password = hash_password(request.newPassword)
    db.commit()

    return {"message": "Password changed successfully."}
