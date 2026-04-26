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
