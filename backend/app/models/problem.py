from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    difficulty: Mapped[str] = mapped_column(String(20), index=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    description: Mapped[str] = mapped_column(Text)
    starter_code: Mapped[dict[str, str]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    test_cases: Mapped[list["TestCase"]] = relationship(
        back_populates="problem",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class TestCase(Base):
    __tablename__ = "test_cases"
    __table_args__ = (
        UniqueConstraint("problem_id", "position", name="uq_test_cases_problem_position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column()
    stdin: Mapped[str] = mapped_column(Text)
    expected_stdout: Mapped[str] = mapped_column(Text)
    is_sample: Mapped[bool] = mapped_column(default=True)

    problem: Mapped[Problem] = relationship(back_populates="test_cases")
