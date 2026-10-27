"""
Database seeder — creates the initial admin user and default content pillars.
Run with: python -m app.db.init_db
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import structlog
from sqlalchemy.future import select

from app.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.content import ContentPillar
from app.models.user import User, UserRole
from app.observability.logging import configure_logging

logger = structlog.get_logger(__name__)

DEFAULT_PILLARS = [
    ("GLP-1 Education", "glp-1-education", "Educational content about GLP-1 medications and how they work"),
    ("Obesity & Metabolic Health", "obesity-metabolic-health", "Science and facts about obesity as a medical condition"),
    ("Nutrition & Lifestyle", "nutrition-lifestyle", "Sustainable nutrition habits and lifestyle changes"),
    ("Exercise & Muscle Preservation", "exercise-muscle-preservation", "Physical activity guidance during weight loss"),
    ("Medical Supervision", "medical-supervision", "Importance of professional medical guidance"),
    ("Myths vs. Evidence", "myths-vs-evidence", "Fact-checking common misconceptions"),
    ("Patient FAQs", "patient-faqs", "Frequently asked questions from patients"),
    ("Healthcare Professional Perspectives", "hcp-perspectives", "Content aimed at or featuring healthcare professionals"),
    ("Brand Education", "brand-education", "How Metago works, its program, and differentiators"),
    ("General Wellness", "general-wellness", "Broader wellness and preventive health content"),
]

DEMO_SOCIAL_ACCOUNTS = [
    ("youtube", "MetagoOfficial_YT", "Metago — Official YouTube"),
    ("instagram", "metago.official", "Metago Official"),
    ("x", "MetagoHealth", "Metago Health"),
]


async def seed_database():
    configure_logging()
    async with AsyncSessionLocal() as db:
        # ── Admin user ──────────────────────────────────────────────
        existing = await db.execute(
            select(User).where(User.email == settings.INITIAL_ADMIN_EMAIL)
        )
        if not existing.scalar_one_or_none():
            admin = User(
                email=settings.INITIAL_ADMIN_EMAIL,
                full_name="Metago Admin",
                hashed_password=hash_password(settings.INITIAL_ADMIN_PASSWORD),
                role=UserRole.SUPER_ADMIN,
                is_active=True,
                is_verified=True,
            )
            db.add(admin)
            logger.info("created_admin_user", email=settings.INITIAL_ADMIN_EMAIL)
        else:
            logger.info("admin_user_exists", email=settings.INITIAL_ADMIN_EMAIL)

        # ── Content pillars ─────────────────────────────────────────
        for i, (name, slug, desc) in enumerate(DEFAULT_PILLARS):
            existing = await db.execute(
                select(ContentPillar).where(ContentPillar.slug == slug)
            )
            if not existing.scalar_one_or_none():
                pillar = ContentPillar(
                    name=name, slug=slug, description=desc, sort_order=i
                )
                db.add(pillar)
                logger.info("created_pillar", name=name)

        # ── Demo social accounts ────────────────────────────────────
        if settings.is_demo:
            from app.models.social import SocialAccount
            for platform, name, display in DEMO_SOCIAL_ACCOUNTS:
                existing = await db.execute(
                    select(SocialAccount).where(SocialAccount.account_name == name)
                )
                if not existing.scalar_one_or_none():
                    account = SocialAccount(
                        platform=platform,
                        account_name=name,
                        display_name=display,
                        is_mock=True,
                        is_active=True,
                        health_status="healthy",
                    )
                    db.add(account)
                    logger.info("created_demo_account", platform=platform, name=name)

        await db.commit()
        logger.info("seed_complete")


if __name__ == "__main__":
    asyncio.run(seed_database())
