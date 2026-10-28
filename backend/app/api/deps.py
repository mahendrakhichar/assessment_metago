"""
FastAPI dependencies — auth, DB session, role checks.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import settings
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.security import decode_access_token, hash_password
from app.db.session import get_db
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


async def _get_or_create_demo_user(db: AsyncSession) -> User:
    """Return the demo admin user when operating in demo mode."""
    result = await db.execute(
        select(User).where(User.email == settings.INITIAL_ADMIN_EMAIL)
    )
    user = result.scalar_one_or_none()
    if user:
        return user

    # Fallback to any active super admin
    result = await db.execute(
        select(User).where(User.role == UserRole.SUPER_ADMIN, User.is_active == True).limit(1)  # noqa: E712
    )
    user = result.scalar_one_or_none()
    if user:
        return user

    # Create initial demo user if database has not been seeded yet
    user = User(
        email=settings.INITIAL_ADMIN_EMAIL,
        full_name="Metago Admin",
        hashed_password=hash_password(settings.INITIAL_ADMIN_PASSWORD),
        role=UserRole.SUPER_ADMIN,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate JWT bearer token; return the authenticated User.

    In demo mode (settings.is_demo is True), automatically falls back to the
    demo admin user when no authorization header is provided or token is invalid.
    """
    if not credentials:
        if settings.is_demo:
            return await _get_or_create_demo_user(db)
        raise AuthenticationError("No authorization header provided")
    try:
        user_id = decode_access_token(credentials.credentials)
    except JWTError:
        if settings.is_demo:
            return await _get_or_create_demo_user(db)
        raise AuthenticationError("Invalid or expired token")

    result = await db.execute(select(User).where(User.id == user_id))  # type: ignore
    user = result.scalar_one_or_none()
    if not user:
        if settings.is_demo:
            return await _get_or_create_demo_user(db)
        raise AuthenticationError("User not found")
    if not user.is_active:
        raise AuthenticationError("Account is inactive")
    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    return user


def require_role(*roles: UserRole):
    """Dependency factory: require one of the specified roles."""

    async def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise PermissionDeniedError(
                f"Required role(s): {', '.join(r.value for r in roles)}"
            )
        return user

    return _check


def require_content_manager():
    return require_role(
        UserRole.SUPER_ADMIN,
        UserRole.ADMIN,
        UserRole.CONTENT_MANAGER,
        UserRole.MEDICAL_REVIEWER,
    )


def require_admin():
    return require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN)


def require_medical_reviewer():
    return require_role(UserRole.SUPER_ADMIN, UserRole.MEDICAL_REVIEWER)
