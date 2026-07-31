from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Language = Literal["python", "java", "cpp"]
SubmissionStatus = Literal[
    "ACCEPTED",
    "WRONG_ANSWER",
    "TIME_LIMIT_EXCEEDED",
    "COMPILE_ERROR",
    "RUNTIME_ERROR",
]


class SubmitCodeRequest(BaseModel):
    language: Language
    code: str = Field(min_length=1)


class TestCaseResultItem(BaseModel):
    position: int
    passed: bool
    is_sample: bool
    stdin: str
    expected_stdout: str
    actual_stdout: str
    stderr: str
    status_description: str


class SubmitCodeResponse(BaseModel):
    submission_id: int
    problem_slug: str
    status: SubmissionStatus
    passed_test_cases: int
    total_test_cases: int
    runtime_ms: int | None = None
    test_results: list[TestCaseResultItem]


class TopicStat(BaseModel):
    tag: str
    attempted: int
    solved: int
    pass_rate: float


class RecentSubmissionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    problem_slug: str
    problem_title: str
    difficulty: str
    language: str
    status: str
    passed_test_cases: int
    total_test_cases: int
    created_at: datetime


class DifficultyBreakdown(BaseModel):
    easy: int = 0
    medium: int = 0
    hard: int = 0


class UserAnalyticsResponse(BaseModel):
    total_solved: int
    solved_by_difficulty: DifficultyBreakdown
    total_submissions: int
    accuracy_rate: float
    topic_stats: list[TopicStat]
    weak_topics: list[str]
    recent_submissions: list[RecentSubmissionItem]
