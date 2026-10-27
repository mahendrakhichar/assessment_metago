"""
RBAC permissions — maps roles to allowed actions.

Design: deterministic permission checks outside the LLM.
All authorization is enforced here, never by AI reasoning.
"""
from enum import Enum as PyEnum

from app.models.user import UserRole


class Action(str, PyEnum):
    # Content
    READ_CONTENT = "read_content"
    CREATE_CONTENT = "create_content"
    EDIT_CONTENT = "edit_content"
    DELETE_CONTENT = "delete_content"
    APPROVE_BRAND = "approve_brand"
    APPROVE_MEDICAL = "approve_medical"
    PUBLISH_CONTENT = "publish_content"
    # Trends
    READ_TRENDS = "read_trends"
    MANAGE_TRENDS = "manage_trends"
    # Accounts
    READ_ACCOUNTS = "read_accounts"
    MANAGE_ACCOUNTS = "manage_accounts"
    PAUSE_ACCOUNTS = "pause_accounts"
    # Analytics
    READ_ANALYTICS = "read_analytics"
    # Users
    MANAGE_USERS = "manage_users"
    # Settings
    MANAGE_SETTINGS = "manage_settings"


# Role → allowed actions mapping
ROLE_PERMISSIONS: dict[UserRole, set[Action]] = {
    UserRole.SUPER_ADMIN: set(Action),  # All actions

    UserRole.ADMIN: {
        Action.READ_CONTENT, Action.CREATE_CONTENT, Action.EDIT_CONTENT,
        Action.DELETE_CONTENT, Action.APPROVE_BRAND,
        Action.READ_TRENDS, Action.MANAGE_TRENDS,
        Action.READ_ACCOUNTS, Action.MANAGE_ACCOUNTS, Action.PAUSE_ACCOUNTS,
        Action.READ_ANALYTICS,
        Action.MANAGE_SETTINGS,
    },

    UserRole.MEDICAL_REVIEWER: {
        Action.READ_CONTENT, Action.EDIT_CONTENT, Action.APPROVE_MEDICAL,
        Action.APPROVE_BRAND, Action.READ_TRENDS, Action.READ_ANALYTICS,
    },

    UserRole.CONTENT_MANAGER: {
        Action.READ_CONTENT, Action.CREATE_CONTENT, Action.EDIT_CONTENT,
        Action.READ_TRENDS, Action.READ_ANALYTICS,
    },

    UserRole.ANALYST: {
        Action.READ_CONTENT, Action.READ_TRENDS, Action.READ_ANALYTICS,
    },

    UserRole.VIEWER: {
        Action.READ_CONTENT, Action.READ_TRENDS, Action.READ_ANALYTICS,
    },
}


def is_allowed(role: UserRole, action: Action) -> bool:
    """Check if a role is permitted to perform an action."""
    return action in ROLE_PERMISSIONS.get(role, set())
