"""Services for question retrieval and selection."""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Chapter, DifficultyLevel, Question, Topic, UserAttempt


def fetch_questions(
    db: Session,
    subject_id: int | None = None,
    chapter_id: int | None = None,
    topic_id: int | None = None,
    difficulty: DifficultyLevel | None = None,
    limit: int = 10,
    randomize: bool = True,
    attempted_only: bool = False,
    unattempted_only: bool = False,
    retry_wrong: bool = False,
) -> list[Question]:
    """Fetch filtered questions using optional attempt-based conditions."""
    query = db.query(Question).join(Topic, Topic.id == Question.topic_id).join(
        Chapter, Chapter.id == Topic.chapter_id
    )

    if subject_id is not None:
        query = query.filter(Chapter.subject_id == subject_id)
    if chapter_id is not None:
        query = query.filter(Topic.chapter_id == chapter_id)
    if topic_id is not None:
        query = query.filter(Question.topic_id == topic_id)
    if difficulty is not None:
        query = query.filter(Question.difficulty == difficulty)

    attempted_question_subq = db.query(UserAttempt.question_id).distinct()
    wrong_question_subq = db.query(UserAttempt.question_id).filter(UserAttempt.is_correct.is_(False)).distinct()

    if attempted_only:
        query = query.filter(Question.id.in_(attempted_question_subq))
    if unattempted_only:
        query = query.filter(~Question.id.in_(attempted_question_subq))
    if retry_wrong:
        query = query.filter(Question.id.in_(wrong_question_subq))

    if randomize:
        query = query.order_by(func.random())
    else:
        query = query.order_by(Question.id.desc())

    sanitized_limit = max(1, limit)
    return query.limit(sanitized_limit).all()


def count_questions(
    db: Session,
    subject_id: int | None = None,
    chapter_id: int | None = None,
    topic_id: int | None = None,
    difficulty: DifficultyLevel | None = None,
    attempted_only: bool = False,
    unattempted_only: bool = False,
    retry_wrong: bool = False,
) -> int:
    """Count questions with same filter logic used by fetch_questions."""
    query = db.query(Question).join(Topic, Topic.id == Question.topic_id).join(
        Chapter, Chapter.id == Topic.chapter_id
    )

    if subject_id is not None:
        query = query.filter(Chapter.subject_id == subject_id)
    if chapter_id is not None:
        query = query.filter(Topic.chapter_id == chapter_id)
    if topic_id is not None:
        query = query.filter(Question.topic_id == topic_id)
    if difficulty is not None:
        query = query.filter(Question.difficulty == difficulty)

    attempted_question_subq = db.query(UserAttempt.question_id).distinct()
    wrong_question_subq = db.query(UserAttempt.question_id).filter(UserAttempt.is_correct.is_(False)).distinct()

    if attempted_only:
        query = query.filter(Question.id.in_(attempted_question_subq))
    if unattempted_only:
        query = query.filter(~Question.id.in_(attempted_question_subq))
    if retry_wrong:
        query = query.filter(Question.id.in_(wrong_question_subq))

    return query.count()
