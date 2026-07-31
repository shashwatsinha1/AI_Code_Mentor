from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.sheet import Sheet, SheetItem, UserSheetProgress
from app.models.user import User
from app.schemas.sheet import (
    PatternSection,
    SheetDetailResponse,
    SheetItemRead,
    SheetListItem,
    ToggleProgressResponse,
)

router = APIRouter()


@router.get("", response_model=list[SheetListItem])
async def list_sheets(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[SheetListItem]:
    sheets_res = await db.execute(select(Sheet).options(selectinload(Sheet.items)))
    sheets = sheets_res.scalars().all()

    # User completed progress map
    progress_res = await db.execute(
        select(UserSheetProgress.sheet_item_id).where(
            UserSheetProgress.user_id == current_user.id,
            UserSheetProgress.is_completed == True,  # noqa: E712
        )
    )
    completed_item_ids = set(progress_res.scalars().all())

    result: list[SheetListItem] = []
    for s in sheets:
        total = len(s.items)
        completed = sum(1 for item in s.items if item.id in completed_item_ids)
        result.append(
            SheetListItem(
                id=s.id,
                slug=s.slug,
                title=s.title,
                description=s.description,
                author=s.author,
                total_questions=total,
                completed_questions=completed,
            )
        )
    return result


@router.get("/{slug}", response_model=SheetDetailResponse)
async def get_sheet_detail(
    slug: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SheetDetailResponse:
    sheet_res = await db.execute(
        select(Sheet).options(selectinload(Sheet.items)).where(Sheet.slug == slug)
    )
    sheet = sheet_res.scalar_one_or_none()
    if sheet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sheet not found")

    progress_res = await db.execute(
        select(UserSheetProgress.sheet_item_id).where(
            UserSheetProgress.user_id == current_user.id,
            UserSheetProgress.is_completed == True,  # noqa: E712
        )
    )
    completed_item_ids = set(progress_res.scalars().all())

    # Group items by pattern
    pattern_map: dict[str, list[SheetItemRead]] = {}
    for item in sorted(sheet.items, key=lambda x: (x.pattern, x.position)):
        is_done = item.id in completed_item_ids
        read_item = SheetItemRead(
            id=item.id,
            pattern=item.pattern,
            position=item.position,
            title=item.title,
            difficulty=item.difficulty,
            platform=item.platform,
            problem_url=item.problem_url,
            article_url=item.article_url,
            problem_slug=item.problem_slug,
            description=item.description,
            is_completed=is_done,
        )
        if item.pattern not in pattern_map:
            pattern_map[item.pattern] = []
        pattern_map[item.pattern].append(read_item)

    pattern_sections: list[PatternSection] = []
    total_questions = len(sheet.items)
    completed_questions = sum(1 for item in sheet.items if item.id in completed_item_ids)

    for pattern_name, items in pattern_map.items():
        pat_total = len(items)
        pat_completed = sum(1 for it in items if it.is_completed)
        pattern_sections.append(
            PatternSection(
                pattern=pattern_name,
                total_count=pat_total,
                completed_count=pat_completed,
                items=items,
            )
        )

    return SheetDetailResponse(
        id=sheet.id,
        slug=sheet.slug,
        title=sheet.title,
        description=sheet.description,
        author=sheet.author,
        total_questions=total_questions,
        completed_questions=completed_questions,
        patterns=pattern_sections,
    )


@router.post("/{slug}/items/{item_id}/toggle", response_model=ToggleProgressResponse)
async def toggle_sheet_item_completion(
    slug: str,
    item_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ToggleProgressResponse:
    item_res = await db.execute(
        select(SheetItem)
        .join(Sheet, SheetItem.sheet_id == Sheet.id)
        .where(Sheet.slug == slug, SheetItem.id == item_id)
    )
    item = item_res.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sheet item not found")

    prog_res = await db.execute(
        select(UserSheetProgress).where(
            UserSheetProgress.user_id == current_user.id,
            UserSheetProgress.sheet_item_id == item_id,
        )
    )
    prog = prog_res.scalar_one_or_none()

    if prog is None:
        prog = UserSheetProgress(
            user_id=current_user.id,
            sheet_item_id=item_id,
            is_completed=True,
        )
        db.add(prog)
        new_completed = True
    else:
        prog.is_completed = not prog.is_completed
        new_completed = prog.is_completed

    await db.commit()

    # Calculate overall total & completed count for sheet
    all_items_res = await db.execute(
        select(SheetItem.id).where(SheetItem.sheet_id == item.sheet_id)
    )
    all_item_ids = all_items_res.scalars().all()
    total_q = len(all_item_ids)

    completed_res = await db.execute(
        select(func.count(UserSheetProgress.id)).where(
            UserSheetProgress.user_id == current_user.id,
            UserSheetProgress.sheet_item_id.in_(all_item_ids),
            UserSheetProgress.is_completed == True,  # noqa: E712
        )
    )
    completed_q = completed_res.scalar() or 0

    return ToggleProgressResponse(
        item_id=item_id,
        is_completed=new_completed,
        completed_questions=completed_q,
        total_questions=total_q,
    )
