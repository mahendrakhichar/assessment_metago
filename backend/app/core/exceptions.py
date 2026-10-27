"""
Core Exceptions — Custom exception classes for the Metago platform.
"""
from fastapi import status


class MetagoException(Exception):
    """Base exception for all Metago-specific errors."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFoundError(MetagoException):
    def __init__(self, resource: str, resource_id: str | None = None):
        detail = f"{resource} not found"
        if resource_id:
            detail = f"{resource} '{resource_id}' not found"
        super().__init__(detail, status_code=status.HTTP_404_NOT_FOUND)


class PermissionDeniedError(MetagoException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(detail, status_code=status.HTTP_403_FORBIDDEN)


class AuthenticationError(MetagoException):
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(detail, status_code=status.HTTP_401_UNAUTHORIZED)


class ConflictError(MetagoException):
    def __init__(self, detail: str):
        super().__init__(detail, status_code=status.HTTP_409_CONFLICT)


class ValidationError(MetagoException):
    def __init__(self, detail: str):
        super().__init__(detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class PublishingBlockedError(MetagoException):
    """Raised when content cannot be published due to compliance or approval rules."""

    def __init__(self, detail: str = "Publishing is blocked pending required review"):
        super().__init__(detail, status_code=status.HTTP_403_FORBIDDEN)


class MedicalReviewRequiredError(MetagoException):
    """Raised when content requires medical review that has not been completed."""

    def __init__(self):
        super().__init__(
            "Medical review is required before this content can be published",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class OperatingModeError(MetagoException):
    """Raised when an action is not permitted in the current operating mode."""

    def __init__(self, action: str, mode: str):
        super().__init__(
            f"Action '{action}' is not permitted in '{mode}' mode",
            status_code=status.HTTP_403_FORBIDDEN,
        )
