"""
Metago AI Marketing Platform — FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.v1 import router as api_v1_router
from app.core.exceptions import MetagoException
from app.observability.logging import configure_logging

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    configure_logging()
    logger.info(
        "metago_startup",
        app_name=settings.APP_NAME,
        env=settings.APP_ENV,
        mode=settings.OPERATING_MODE,
    )
    yield
    logger.info("metago_shutdown")


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-powered marketing automation and distribution platform for Metago.",
        version="0.1.0",
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
        openapi_url="/api/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ── Routes ────────────────────────────────────────────────────────
    app.include_router(api_v1_router, prefix="/api/v1")

    # ── Exception Handlers ────────────────────────────────────────────
    @app.exception_handler(MetagoException)
    async def metago_exception_handler(request, exc: MetagoException):
        logger.warning("metago_exception", detail=exc.detail, status_code=exc.status_code)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    # ── Health Check ─────────────────────────────────────────────────
    @app.get("/health", tags=["health"], summary="Health check")
    async def health():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "env": settings.APP_ENV,
            "mode": settings.OPERATING_MODE,
        }

    return app


app = create_application()
