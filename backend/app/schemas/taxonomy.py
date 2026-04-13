"""Schemas for subject/chapter/topic resources."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class SubjectRead(ORMBase):
    id: int
    name: str


class ChapterCreate(BaseModel):
    subject_id: int
    name: str = Field(..., min_length=1, max_length=255)


class ChapterRead(ORMBase):
    id: int
    subject_id: int
    name: str


class TopicCreate(BaseModel):
    chapter_id: int
    name: str = Field(..., min_length=1, max_length=255)


class TopicRead(ORMBase):
    id: int
    chapter_id: int
    name: str

