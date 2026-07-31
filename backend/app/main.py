from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, drafts, execute, mentor, problems, sheets, users
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import draft, problem, refresh_token, sheet, submission, user  # noqa: F401
from app.seed.problems import seed_problems
from app.seed.sheets import seed_sheets


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    from app.db.session import SessionLocal

    async with SessionLocal() as session:
        await seed_problems(session)
        await seed_sheets(session)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(drafts.router, prefix="/drafts", tags=["drafts"])
app.include_router(execute.router, prefix="/execute", tags=["execute"])
app.include_router(mentor.router, tags=["mentor"])
app.include_router(problems.router, prefix="/problems", tags=["problems"])
app.include_router(sheets.router, prefix="/sheets", tags=["sheets"])
app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
