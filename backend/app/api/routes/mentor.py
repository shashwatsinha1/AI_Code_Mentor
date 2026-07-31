from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.mentor import HintRequest, MentorCodeRequest, MentorResponse
from app.services.ai_mentor import ai_mentor_service

router = APIRouter()


@router.post("/explain", response_model=MentorResponse)
async def explain_code(
    payload: MentorCodeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> MentorResponse:
    return await ai_mentor_service.explain(payload)


@router.post("/hint", response_model=MentorResponse)
async def generate_hint(
    payload: HintRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> MentorResponse:
    return await ai_mentor_service.hint(payload)


@router.post("/detect-bugs", response_model=MentorResponse)
async def detect_bugs(
    payload: MentorCodeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> MentorResponse:
    return await ai_mentor_service.detect_bugs(payload)


@router.post("/complexity", response_model=MentorResponse)
async def analyze_complexity(
    payload: MentorCodeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> MentorResponse:
    return await ai_mentor_service.complexity(payload)


@router.post("/optimize", response_model=MentorResponse)
async def optimize_code(
    payload: MentorCodeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> MentorResponse:
    return await ai_mentor_service.optimize(payload)
