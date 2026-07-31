from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Sheet(Base):
    __tablename__ = "sheets"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(80), default="Striver / Fraz")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    items: Mapped[list["SheetItem"]] = relationship(
        back_populates="sheet",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SheetItem(Base):
    __tablename__ = "sheet_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sheet_id: Mapped[int] = mapped_column(ForeignKey("sheets.id", ondelete="CASCADE"), index=True)
    pattern: Mapped[str] = mapped_column(String(100), index=True)
    position: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String(160))
    difficulty: Mapped[str] = mapped_column(String(20))
    platform: Mapped[str] = mapped_column(String(40))  # leetcode, codeforces, gfg
    problem_url: Mapped[str] = mapped_column(Text)
    article_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    problem_slug: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    sheet: Mapped[Sheet] = relationship(back_populates="items")


class UserSheetProgress(Base):
    __tablename__ = "user_sheet_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "sheet_item_id", name="uq_user_sheet_item_progress"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    sheet_item_id: Mapped[int] = mapped_column(
        ForeignKey("sheet_items.id", ondelete="CASCADE"), index=True
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
