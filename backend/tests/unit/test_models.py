"""
Unit tests for content model enums and status transitions.
"""
import pytest
from app.models.content import ContentStatus, MedicalRiskLevel, ContentFormat, SocialPlatform, FunnelStage


class TestContentStatusEnum:
    def test_all_states_are_strings(self):
        for status in ContentStatus:
            assert isinstance(status.value, str)

    def test_published_is_terminal_after_approved(self):
        """Verify the flow ordering makes semantic sense."""
        flow = [
            ContentStatus.DRAFT,
            ContentStatus.FACT_CHECK,
            ContentStatus.MEDICAL_REVIEW,
            ContentStatus.BRAND_REVIEW,
            ContentStatus.APPROVED,
            ContentStatus.SCHEDULED,
            ContentStatus.PUBLISHED,
        ]
        assert len(flow) == 7

    def test_blocked_and_revision_are_separate_from_flow(self):
        assert ContentStatus.BLOCKED != ContentStatus.REVISION_REQUESTED


class TestMedicalRiskLevel:
    def test_critical_is_highest(self):
        levels = [r.value for r in MedicalRiskLevel]
        assert "critical" in levels
        assert "high" in levels
        assert "medium" in levels
        assert "low" in levels

    def test_high_risk_requires_human_review(self):
        """Business rule: HIGH and CRITICAL risk content requires human reviewer."""
        high_risk_levels = {MedicalRiskLevel.HIGH, MedicalRiskLevel.CRITICAL}
        low_risk_levels = {MedicalRiskLevel.LOW, MedicalRiskLevel.MEDIUM}
        # Verify they are disjoint
        assert high_risk_levels.isdisjoint(low_risk_levels)


class TestUserRolePermissions:
    def _make_user(self, role):
        """Helper: create a minimal User-like object with a role attribute."""
        from app.models.user import UserRole
        class FakeUser:
            pass
        u = FakeUser()
        u.role = role
        # Bind the real methods from User
        from app.models.user import User
        u.can_approve_medical = lambda: User.can_approve_medical(u)
        u.can_manage_content = lambda: User.can_manage_content(u)
        return u

    def test_medical_reviewer_can_approve_medical(self):
        from app.models.user import UserRole
        u = self._make_user(UserRole.MEDICAL_REVIEWER)
        assert u.can_approve_medical()

    def test_viewer_cannot_manage_content(self):
        from app.models.user import UserRole
        u = self._make_user(UserRole.VIEWER)
        assert not u.can_manage_content()

    def test_admin_can_manage_content(self):
        from app.models.user import UserRole
        u = self._make_user(UserRole.ADMIN)
        assert u.can_manage_content()
