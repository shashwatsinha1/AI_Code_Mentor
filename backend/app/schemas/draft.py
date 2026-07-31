from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.language import Language, normalize_language


class DraftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    language: Language
    code: str
    updated_at: datetime


class DraftUpsert(BaseModel):
    language: Language
    code: str

    @field_validator("language", mode="before")
    @classmethod
    def normalize_language_value(cls, value: str) -> Language:
        return normalize_language(value)
