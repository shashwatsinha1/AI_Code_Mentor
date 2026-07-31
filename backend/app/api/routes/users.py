from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.submission import UserAnalyticsResponse
from app.schemas.user import UserRead
from app.services.evaluator import problem_evaluator_service

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def read_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserRead:
    return UserRead.model_validate(current_user)


@router.get("/me/analytics", response_model=UserAnalyticsResponse)
async def read_user_analytics(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserAnalyticsResponse:
    return await problem_evaluator_service.get_user_analytics(db, current_user)
