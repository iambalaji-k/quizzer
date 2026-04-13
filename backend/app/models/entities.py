"""SQLAlchemy entities for quiz domain."""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DifficultyLevel(str, enum.Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    chapters: Mapped[list["Chapter"]] = relationship(
        "Chapter", back_populates="subject", cascade="all, delete-orphan"
    )


class Chapter(Base):
    __tablename__ = "chapters"
    __table_args__ = (UniqueConstraint("subject_id", "name", name="uq_chapter_subject_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    subject: Mapped["Subject"] = relationship("Subject", back_populates="chapters")
    topics: Mapped[list["Topic"]] = relationship(
        "Topic", back_populates="chapter", cascade="all, delete-orphan"
    )


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (UniqueConstraint("chapter_id", "name", name="uq_topic_chapter_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="topics")
    questions: Mapped[list["Question"]] = relationship(
        "Question", back_populates="topic", cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, name="difficulty_level"),
        nullable=False,
        index=True,
    )
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    topic: Mapped["Topic"] = relationship("Topic", back_populates="questions")
    options: Mapped[list["Option"]] = relationship(
        "Option", back_populates="question", cascade="all, delete-orphan"
    )
    attempts: Mapped[list["UserAttempt"]] = relationship("UserAttempt", back_populates="question")

    @property
    def topic_name(self) -> str | None:
        return self.topic.name if self.topic else None

    @property
    def chapter_id(self) -> int | None:
        return self.topic.chapter_id if self.topic else None

    @property
    def chapter_name(self) -> str | None:
        return self.topic.chapter.name if self.topic and self.topic.chapter else None

    @property
    def subject_id(self) -> int | None:
        if not self.topic or not self.topic.chapter:
            return None
        return self.topic.chapter.subject_id

    @property
    def subject_name(self) -> str | None:
        if not self.topic or not self.topic.chapter or not self.topic.chapter.subject:
            return None
        return self.topic.chapter.subject.name


class Option(Base):
    __tablename__ = "options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False, index=True)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    question: Mapped["Question"] = relationship("Question", back_populates="options")
    selected_in_attempts: Mapped[list["UserAttempt"]] = relationship("UserAttempt", back_populates="selected_option")


class UserAttempt(Base):
    __tablename__ = "user_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False, index=True)
    selected_option_id: Mapped[int] = mapped_column(ForeignKey("options.id"), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    marked_for_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    question: Mapped["Question"] = relationship("Question", back_populates="attempts")
    selected_option: Mapped["Option"] = relationship("Option", back_populates="selected_in_attempts")
