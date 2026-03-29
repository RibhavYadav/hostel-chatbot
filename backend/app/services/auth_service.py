import os
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

# HTTPBearer reads the token from the Authorization header
security = HTTPBearer()


# Password hashing
def hash_password(plain_password: str) -> str:
    """
    Hashes a plain text password using bcrypt.
    A random salt is generated on every call so two identical
    passwords produce different hashes.
    Returns the hash string.
    """
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a stored bcrypt hash.
    bcrypt re-hashes the plain password using the salt embedded
    in the stored hash and compares the results.
    Returns bool.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# Student JWT
def create_access_token(registration_number: int) -> str:
    """
    Creates a signed JWT token for a student.
    The registration number is stored as the subject claim.
    Token expires after JWT_EXPIRE_MINUTES (default 24 hours).
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": str(registration_number), "exp": expire}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int:
    """
    Decodes and verifies a student JWT token.
    Returns the registration number as an int if the token is valid.
    Raises JWTError if the token is invalid, expired, or missing the subject claim.
    """
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    registration_number = payload.get("sub")
    if registration_number is None:
        raise JWTError("Token has no subject claim.")
    return int(registration_number)


def get_current_student(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency for student protected routes.
    Extracts the bearer token from the Authorization header,
    decodes it and returns the Student object from the database.
    Raises 401 if the token is missing, invalid, expired, or the student account does not exist.
    """
    from app.models.db_models import Student

    try:
        registration_number = decode_access_token(credentials.credentials)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    student = db.query(Student).filter(Student.registration_number == registration_number).first()
    if student is None:
        raise HTTPException(status_code=401, detail="Student account not found.")

    return student


# Admin JWT
def create_admin_token(email: str, admin_team: str) -> str:
    """
    Creates a signed JWT token for an admin.
    Email is stored as the subject claim.
    admin_team is stored as the team claim so permission checks
    can read the team directly from the token without a database query.
    Token expires after JWT_EXPIRE_MINUTES (default 24 hours).
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": email,
        "team": admin_team,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency for admin protected routes.
    Extracts the bearer token from the Authorization header,
    decodes it and verifies both the email subject claim and
    the team claim are present. Returns the Admin object.
    Raises 401 if the token is missing, invalid, expired,
    missing required claims, or the admin account does not exist.
    """
    from app.models.db_models import Admin

    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        team = payload.get("team")
        if email is None or team is None:
            raise JWTError("Token missing required claims.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    admin = db.query(Admin).filter(Admin.email == email).first()
    if admin is None:
        raise HTTPException(status_code=401, detail="Admin account not found.")

    return admin


# Permission check
def require_teams(*teams):
    """
    FastAPI dependency factory for team-based permission checks.
    Takes one or more team names as arguments and returns a dependency
    that verifies the authenticated admin belongs to one of those teams.
    Raises 403 if the admin's team is not in the allowed list.
    Usage: Depends(require_teams('cso', 'warden'))
    """

    def dependency(current_admin=Depends(get_current_admin)):
        if current_admin.admin_team not in teams:
            raise HTTPException(
                status_code=403, detail=f"Access restricted. Required team: {', '.join(teams)}."
            )
        return current_admin

    return dependency
