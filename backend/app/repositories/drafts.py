from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.draft import Draft


async def get_draft(db: AsyncSession, user_id: int, language: str) -> Draft | None:
    result = await db.execute(
        select(Draft).where(Draft.user_id == user_id, Draft.language == language)
    )
    return result.scalar_one_or_none()


async def upsert_draft(db: AsyncSession, user_id: int, language: str, code: str) -> Draft:
    draft = await get_draft(db, user_id, language)
    if draft is None:
        draft = Draft(user_id=user_id, language=language, code=code)
        db.add(draft)
    else:
        draft.code = code

    await db.commit()
    await db.refresh(draft)
    return draft
