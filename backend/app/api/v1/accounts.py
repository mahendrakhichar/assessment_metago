"""
Social Accounts API — Connected account management, mock publishing.
"""
import uuid
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_user, require_admin
from app.config import settings
from app.core.exceptions import NotFoundError, OperatingModeError
from app.db.session import get_db
from app.models.social import SocialAccount
from app.schemas.social import AccountCreate, AccountResponse

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/", response_model=list[AccountResponse])
async def list_accounts(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    result = await db.execute(
        select(SocialAccount).where(SocialAccount.is_active == True).order_by(  # noqa: E712
            SocialAccount.created_at
        )
    )
    return [AccountResponse.model_validate(a) for a in result.scalars().all()]


@router.post("/", response_model=AccountResponse, status_code=201)
async def create_account(
    body: AccountCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin()),
):
    """Create a social account record. In demo mode, always marks as mock."""
    is_mock = settings.is_demo or body.is_mock
    account = SocialAccount(
        platform=body.platform,
        account_name=body.account_name,
        display_name=body.display_name,
        is_mock=is_mock,
    )
    db.add(account)
    await db.flush()
    await db.refresh(account)
    logger.info(
        "account_created",
        account_id=str(account.id),
        platform=body.platform,
        is_mock=is_mock,
    )
    return AccountResponse.model_validate(account)


@router.post("/{account_id}/pause", status_code=204)
async def pause_account(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin()),
):
    """Emergency pause — stops all outgoing publishing for this account."""
    result = await db.execute(select(SocialAccount).where(SocialAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise NotFoundError("Account", str(account_id))
    account.is_paused = True
    logger.warning("account_paused", account_id=str(account_id))


@router.post("/{account_id}/resume", status_code=204)
async def resume_account(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin()),
):
    result = await db.execute(select(SocialAccount).where(SocialAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise NotFoundError("Account", str(account_id))
    account.is_paused = False
    logger.info("account_resumed", account_id=str(account_id))
