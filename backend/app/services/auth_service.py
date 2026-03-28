import os
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db

# JWT tokens and auth
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(plain_password: str) -> str:
    """Hash a plain text password using bcrypt. Returns the hash string."""
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plain password against a stored bcrypt hash. Returns bool."""
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(registration_number: int) -> str:
    """
    Creates a signed JWT token for the registration number.
    Token expires after JWT_EXPIRE_MINUTES.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": str(registration_number), "exp": expire}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int:
    """
    Decodes and verifies JWT token.
    Returns the registration number if valid.
    Raises JWTError if the token is invalid or expired.
    """
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    registration_number = payload.get("sub")
    if registration_number is None:
        raise JWTError("Token has no subject claim.")
    return int(registration_number)


def get_current_student(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    FastAPI dependency for secure routes.
    Reads the JWT token from the authorization header, decodes it and returns the student object from the database.
    Raises error 401 if the token is missing, invalid or expired.
    """
    from app.models.db_models import Student

    try:
        registration_number = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    student = db.query(Student).filter(Student.registration_number == registration_number).first()
    if student is None:
        raise HTTPException(status_code=401, detail="Student account not found.")

    return student


def create_admin_token(email: str, admin_team: str) -> str:
    """
    Creates a signed JWT token for the admin.
    Email is used as subject claim and admin_team as team claim.
    The team claim is used on admin endpoints without a database lookup.
    Token expires after JWT_EXPIRE_MINUTES.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": email,
        "team": admin_team,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    FastAPI dependency for admin protected routes.
    Decodes the JWT token from the Authorization header.
    Reads the email from the subject claim and looks up the Admin record.
    Raises 401 if the token is invalid, expired, or the admin is not found.
    """
    from app.models.db_models import Admin

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
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


def require_teams(*teams):
    """
    FastAPI dependency factory for team-based permission checks.
    Returns a dependency that raises 403 if the current admin's team is not in the allowed teams list.
    Usage: Depends(require_teams('cso', 'warden'))
    """

    def dependency(current_admin=Depends(get_current_admin)):
        if current_admin.admin_team not in teams:
            raise HTTPException(
                status_code=403, detail=f"Access restricted. Required team: {', '.join(teams)}."
            )
        return current_admin

    return dependency
