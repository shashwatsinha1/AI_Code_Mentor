from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_refresh_token, new_refresh_token
from app.models.refresh_token import RefreshToken


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


async def create_refresh_token(db: AsyncSession, user_id: int) -> str:
    token = new_refresh_token()
    db.add(
        RefreshToken(
            id=uuid4().hex,
            user_id=user_id,
            token_hash=hash_refresh_token(token),
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_days),
        )
    )
    await db.commit()
    return token


async def rotate_refresh_token(db: AsyncSession, token: str) -> tuple[int, str] | None:
    token_hash = hash_refresh_token(token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    existing = result.scalar_one_or_none()

    if (
        existing is None
        or existing.revoked_at is not None
        or _as_utc(existing.expires_at) <= datetime.now(UTC)
    ):
        return None

    existing.revoked_at = datetime.now(UTC)
    user_id = existing.user_id
    new_token = new_refresh_token()
    db.add(
        RefreshToken(
            id=uuid4().hex,
            user_id=user_id,
            token_hash=hash_refresh_token(new_token),
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_days),
        )
    )
    await db.commit()
    return user_id, new_token
