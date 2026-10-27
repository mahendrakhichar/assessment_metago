"""
API v1 Router — aggregates all route modules.
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.content import router as content_router
from app.api.v1.trends import router as trends_router
from app.api.v1.accounts import router as accounts_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.publishing import router as publishing_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(content_router)
router.include_router(trends_router)
router.include_router(accounts_router)
router.include_router(analytics_router)
router.include_router(publishing_router)
