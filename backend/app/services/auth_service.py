import os
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db


# Password hashing
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


# JWT tokens
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))


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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


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
