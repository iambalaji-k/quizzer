"""Schemas for attempts and analytics."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models import DifficultyLevel
from app.schemas.common import ORMBase


class AttemptCreate(BaseModel):
    question_id: int
    selected_option_id: int
    marked_for_review: bool = False


class AttemptRead(ORMBase):
    id: int
    question_id: int
    selected_option_id: int
    is_correct: bool
    marked_for_review: bool
    timestamp: datetime


class AttemptResult(BaseModel):
    attempt_id: int
    is_correct: bool
    correct_option_id: int
    explanation: str


class TopicAccuracy(BaseModel):
    topic_id: int
    topic_name: str
    chapter_name: str
    subject_name: str
    attempted: int
    correct: int
    accuracy: float


class DifficultyAccuracy(BaseModel):
    difficulty: DifficultyLevel
    attempted: int
    correct: int
    accuracy: float


class StatsResponse(BaseModel):
    total_questions: int = Field(default=0)
    total_attempted: int = Field(default=0)
    total_correct: int = Field(default=0)
    total_wrong: int = Field(default=0)
    unattempted_questions: int = Field(default=0)
    marked_for_review_count: int = Field(default=0)
    attempted_subjects_count: int = Field(default=0)
    attempted_chapters_count: int = Field(default=0)
    attempted_topics_count: int = Field(default=0)
    accuracy_percentage: float = Field(default=0.0)
    topic_wise_accuracy: list[TopicAccuracy] = Field(default_factory=list)
    difficulty_wise_accuracy: list[DifficultyAccuracy] = Field(default_factory=list)
    weak_topics: list[TopicAccuracy] = Field(default_factory=list)


class ReviewAttempt(BaseModel):
    attempt_id: int
    question_id: int
    question_text: str
    selected_option_id: int
    selected_option_text: str
    correct_option_id: int
    correct_option_text: str
    is_correct: bool
    marked_for_review: bool
    difficulty: DifficultyLevel
    explanation: str
    topic_id: int
    topic_name: str
    timestamp: datetime
