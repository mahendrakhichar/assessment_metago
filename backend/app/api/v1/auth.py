"""
Auth API — Login, refresh, register, current user.
"""
import hashlib
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_user
from app.config import settings
from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.user import RefreshToken, User, UserRole
from app.schemas.auth import (
    LoginResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user account. First registered user gets ADMIN role."""
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise ConflictError("An account with this email already exists")

    # First user becomes super admin
    count_result = await db.execute(select(User))
    is_first_user = count_result.scalars().first() is None

    user = User(
        email=body.email,
        full_name=body.full_name,
        hashed_password=hash_password(body.password),
        role=UserRole.SUPER_ADMIN if is_first_user else UserRole.VIEWER,
        is_verified=is_first_user,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    logger.info("user_registered", user_id=str(user.id), email=user.email)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Authenticate with email + password; returns access + refresh tokens."""
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise AuthenticationError("Invalid email or password")
    if not user.is_active:
        raise AuthenticationError("Account is inactive")

    access_token = create_access_token(str(user.id), {"role": user.role})
    refresh_token = create_refresh_token(str(user.id))
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    rt = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=(
            datetime.now(timezone.utc).isoformat()
        ),
    )
    db.add(rt)
    logger.info("user_login", user_id=str(user.id))
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a refresh token for a new access token."""
    from jose import JWTError

    try:
        user_id = decode_refresh_token(body.refresh_token)
    except JWTError:
        raise AuthenticationError("Invalid or expired refresh token")

    token_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,  # noqa: E712
        )
    )
    rt = result.scalar_one_or_none()
    if not rt:
        raise AuthenticationError("Refresh token not found or revoked")

    user_result = await db.execute(select(User).where(User.id == user_id))  # type: ignore
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")

    access_token = create_access_token(str(user.id), {"role": user.role})
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/logout", status_code=204)
async def logout(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Revoke a refresh token."""
    token_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    rt = result.scalar_one_or_none()
    if rt:
        rt.revoked = True


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return UserResponse.model_validate(user)
