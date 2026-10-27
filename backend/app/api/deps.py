"""
FastAPI dependencies — auth, DB session, role checks.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate JWT bearer token; return the authenticated User."""
    if not credentials:
        raise AuthenticationError("No authorization header provided")
    try:
        user_id = decode_access_token(credentials.credentials)
    except JWTError:
        raise AuthenticationError("Invalid or expired token")

    result = await db.execute(select(User).where(User.id == user_id))  # type: ignore
    user = result.scalar_one_or_none()
    if not user:
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
