from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.problem import Problem


async def list_problems(
    db: AsyncSession,
    difficulty: str | None = None,
    tag: str | None = None,
) -> list[Problem]:
    statement = select(Problem).order_by(Problem.difficulty, Problem.title)
    if difficulty:
        statement = statement.where(Problem.difficulty == difficulty)

    result = await db.execute(statement)
    problems = list(result.scalars().all())
    if tag:
        normalized_tag = tag.lower()
        problems = [problem for problem in problems if normalized_tag in problem.tags]
    return problems


async def get_problem_by_slug(db: AsyncSession, slug: str) -> Problem | None:
    result = await db.execute(
        select(Problem).options(selectinload(Problem.test_cases)).where(Problem.slug == slug)
    )
    return result.scalar_one_or_none()
