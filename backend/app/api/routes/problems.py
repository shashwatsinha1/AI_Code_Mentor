from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.problems import get_problem_by_slug, list_problems
from app.schemas.problem import Difficulty, ProblemListItem, ProblemRead
from app.schemas.submission import SubmitCodeRequest, SubmitCodeResponse
from app.services.evaluator import problem_evaluator_service

router = APIRouter()


@router.get("", response_model=list[ProblemListItem])
async def read_problems(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    difficulty: Difficulty | None = None,
    tag: str | None = Query(default=None, min_length=1, max_length=40),
) -> list[ProblemListItem]:
    problems = await list_problems(db, difficulty=difficulty, tag=tag)
    return [ProblemListItem.model_validate(problem) for problem in problems]


@router.get("/{slug}", response_model=ProblemRead)
async def read_problem(
    slug: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProblemRead:
    problem = await get_problem_by_slug(db, slug)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return ProblemRead.model_validate(problem)


@router.post("/{slug}/submit", response_model=SubmitCodeResponse)
async def submit_problem(
    slug: str,
    payload: SubmitCodeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SubmitCodeResponse:
    problem = await get_problem_by_slug(db, slug)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")
    return await problem_evaluator_service.evaluate_and_submit(db, current_user, problem, payload)
