from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

Difficulty = Literal["easy", "medium", "hard"]


class TestCaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    stdin: str
    expected_stdout: str
    is_sample: bool


class ProblemListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    difficulty: Difficulty
    tags: list[str]
    created_at: datetime


class ProblemRead(ProblemListItem):
    description: str
    starter_code: dict[str, str]
    test_cases: list[TestCaseRead]
