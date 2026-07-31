from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.drafts import get_draft, upsert_draft
from app.schemas.draft import DraftRead, DraftUpsert
from app.schemas.language import normalize_language

router = APIRouter()


@router.get("/{language}", response_model=DraftRead | None)
async def read_draft(
    language: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DraftRead | None:
    language = normalize_language(language)
    draft = await get_draft(db, current_user.id, language)
    if draft is None:
        return None
    return DraftRead.model_validate(draft)


@router.put("", response_model=DraftRead)
async def save_draft(
    payload: DraftUpsert,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DraftRead:
    draft = await upsert_draft(db, current_user.id, payload.language, payload.code)
    return DraftRead.model_validate(draft)
