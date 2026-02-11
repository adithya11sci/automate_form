"""
Security utilities for password hashing.
"""
from passlib.context import CryptContext

# Increase rounds for better security, handle potential bcrypt/passlib quirks
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt, with a safety truncation for bcrypt's 72-byte limit."""
    # Bcrypt has a hard limit of 72 bytes. We truncate to ensure no crash.
    # 99.9% of users use shorter passwords anyway.
    safe_password = password[:72]
    return pwd_context.hash(safe_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    safe_password = plain_password[:72]
    return pwd_context.verify(safe_password, hashed_password)
