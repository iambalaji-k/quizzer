"""Schemas for question and option resources."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.models import DifficultyLevel
from app.schemas.common import ORMBase


class OptionCreate(BaseModel):
    option_text: str = Field(..., min_length=1)
    is_correct: bool


class OptionRead(ORMBase):
    id: int
    question_id: int
    option_text: str
    is_correct: bool


class QuestionCreate(BaseModel):
    topic_id: int
    question_text: str = Field(..., min_length=1)
    difficulty: DifficultyLevel
    explanation: str = Field(..., min_length=1)
    options: list[OptionCreate] = Field(..., min_length=2)

    @field_validator("options")
    @classmethod
    def validate_options(cls, value: list[OptionCreate]) -> list[OptionCreate]:
        """Ensure exactly one correct answer is provided."""
        if len(value) < 2:
            raise ValueError("At least two options are required.")
        if sum(1 for option in value if option.is_correct) != 1:
            raise ValueError("Exactly one option must be marked as correct.")
        return value


class QuestionUpdate(BaseModel):
    topic_id: int
    question_text: str = Field(..., min_length=1)
    difficulty: DifficultyLevel
    explanation: str = Field(..., min_length=1)
    options: list[OptionCreate] = Field(..., min_length=2)

    @field_validator("options")
    @classmethod
    def validate_options(cls, value: list[OptionCreate]) -> list[OptionCreate]:
        if len(value) < 2:
            raise ValueError("At least two options are required.")
        if sum(1 for option in value if option.is_correct) != 1:
            raise ValueError("Exactly one option must be marked as correct.")
        return value


class QuestionRead(ORMBase):
    id: int
    topic_id: int
    topic_name: str | None = None
    chapter_id: int | None = None
    chapter_name: str | None = None
    subject_id: int | None = None
    subject_name: str | None = None
    question_text: str
    difficulty: DifficultyLevel
    explanation: str
    options: list[OptionRead]
