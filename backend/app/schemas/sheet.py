from pydantic import BaseModel, ConfigDict


class SheetListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    description: str
    author: str
    total_questions: int = 0
    completed_questions: int = 0


class SheetItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pattern: str
    position: int
    title: str
    difficulty: str
    platform: str
    problem_url: str
    article_url: str | None = None
    problem_slug: str | None = None
    description: str | None = None
    is_completed: bool = False


class PatternSection(BaseModel):
    pattern: str
    total_count: int
    completed_count: int
    items: list[SheetItemRead]


class SheetDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    description: str
    author: str
    total_questions: int
    completed_questions: int
    patterns: list[PatternSection]


class ToggleProgressResponse(BaseModel):
    item_id: int
    is_completed: bool
    completed_questions: int
    total_questions: int
