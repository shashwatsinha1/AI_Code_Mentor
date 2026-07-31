from pydantic import BaseModel, Field, field_validator

from app.schemas.language import Language, normalize_language


class ExecuteRequest(BaseModel):
    language: Language
    code: str = Field(max_length=50_000)
    stdin: str | None = Field(default=None, max_length=20_000)

    @field_validator("language", mode="before")
    @classmethod
    def normalize_language_value(cls, value: str) -> Language:
        return normalize_language(value)


class ExecuteResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool = False
