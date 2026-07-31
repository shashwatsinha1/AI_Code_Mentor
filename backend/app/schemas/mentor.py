from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.language import Language, normalize_language


class MentorCodeRequest(BaseModel):
    language: Language
    code: str = Field(max_length=50_000)
    problem_statement: str | None = Field(default=None, max_length=20_000)
    stdin: str | None = Field(default=None, max_length=20_000)
    stdout: str | None = Field(default=None, max_length=20_000)
    stderr: str | None = Field(default=None, max_length=20_000)
    exit_code: int | None = None

    @field_validator("language", mode="before")
    @classmethod
    def normalize_language_value(cls, value: str) -> Language:
        return normalize_language(value)


class HintRequest(MentorCodeRequest):
    hint_level: Literal[1, 2, 3, 4] = 1


class MentorResponse(BaseModel):
    result: str
    source: Literal["openai", "local"]
