"""
Security — JWT token management, password hashing, credential encryption.
"""
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any

from cryptography.fernet import Fernet
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Use argon2 for password hashing (bcrypt 5.x has passlib compatibility issues)
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


# ── Password ────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT ─────────────────────────────────────────────────────────────────
def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token. Raises JWTError on failure."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def decode_access_token(token: str) -> str:
    """Returns subject (user_id) or raises JWTError."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise JWTError("Invalid token type")
        sub = payload.get("sub")
        if not sub:
            raise JWTError("Missing subject")
        return sub
    except JWTError:
        raise


def decode_refresh_token(token: str) -> str:
    """Returns subject (user_id) or raises JWTError."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")
        sub = payload.get("sub")
        if not sub:
            raise JWTError("Missing subject")
        return sub
    except JWTError:
        raise


# ── Credential Encryption ────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    """Returns a cached Fernet instance using the configured encryption key.
    
    Cached so encrypt/decrypt always use the same key within a process.
    """
    key = settings.ENCRYPTION_KEY
    import base64
    import hashlib
    # Derive a stable Fernet key from the config value using SHA-256
    raw = hashlib.sha256(key.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(raw))


def encrypt_credential(value: str) -> str:
    """Encrypt a credential value for storage."""
    f = _get_fernet()
    return f.encrypt(value.encode()).decode()


def decrypt_credential(encrypted: str) -> str:
    """Decrypt a stored credential value."""
    f = _get_fernet()
    return f.decrypt(encrypted.encode()).decode()
