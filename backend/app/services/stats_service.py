"""Services to compute dynamic analytics from user attempts."""

from __future__ import annotations

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models import Chapter, DifficultyLevel, Question, Subject, Topic, UserAttempt
from app.schemas.attempt import DifficultyAccuracy, StatsResponse, TopicAccuracy


def compute_stats(db: Session) -> StatsResponse:
    """Compute total accuracy and grouped analytics."""
    total_questions = db.query(func.count(Question.id)).scalar() or 0
    total_attempted = db.query(func.count(UserAttempt.id)).scalar() or 0
    unique_attempted_questions = db.query(func.count(func.distinct(UserAttempt.question_id))).scalar() or 0
    correct_count = db.query(func.count(UserAttempt.id)).filter(UserAttempt.is_correct.is_(True)).scalar() or 0
    total_wrong = total_attempted - correct_count
    unattempted_questions = max(total_questions - unique_attempted_questions, 0)
    marked_for_review_count = (
        db.query(func.count(UserAttempt.id)).filter(UserAttempt.marked_for_review.is_(True)).scalar() or 0
    )

    overall_accuracy = round((correct_count / total_attempted) * 100, 2) if total_attempted else 0.0

    topic_rows = (
        db.query(
            Topic.id.label("topic_id"),
            Topic.name.label("topic_name"),
            Chapter.name.label("chapter_name"),
            Subject.name.label("subject_name"),
            func.count(UserAttempt.id).label("attempted"),
            func.sum(case((UserAttempt.is_correct.is_(True), 1), else_=0)).label("correct"),
        )
        .join(Question, Question.topic_id == Topic.id)
        .join(Chapter, Chapter.id == Topic.chapter_id)
        .join(Subject, Subject.id == Chapter.subject_id)
        .join(UserAttempt, UserAttempt.question_id == Question.id)
        .group_by(Topic.id, Topic.name, Chapter.name, Subject.name)
        .all()
    )

    topic_wise = [
        TopicAccuracy(
            topic_id=row.topic_id,
            topic_name=row.topic_name,
            chapter_name=row.chapter_name,
            subject_name=row.subject_name,
            attempted=row.attempted,
            correct=int(row.correct or 0),
            accuracy=round((int(row.correct or 0) / row.attempted) * 100, 2) if row.attempted else 0.0,
        )
        for row in topic_rows
    ]
    weak_topics = sorted(topic_wise, key=lambda x: x.accuracy)[:5]

    difficulty_rows = (
        db.query(
            Question.difficulty.label("difficulty"),
            func.count(UserAttempt.id).label("attempted"),
            func.sum(case((UserAttempt.is_correct.is_(True), 1), else_=0)).label("correct"),
        )
        .join(UserAttempt, UserAttempt.question_id == Question.id)
        .group_by(Question.difficulty)
        .all()
    )

    difficulty_wise = [
        DifficultyAccuracy(
            difficulty=row.difficulty if isinstance(row.difficulty, DifficultyLevel) else DifficultyLevel(row.difficulty),
            attempted=row.attempted,
            correct=int(row.correct or 0),
            accuracy=round((int(row.correct or 0) / row.attempted) * 100, 2) if row.attempted else 0.0,
        )
        for row in difficulty_rows
    ]

    attempted_subjects_count = (
        db.query(func.count(func.distinct(Subject.id)))
        .join(Chapter, Chapter.subject_id == Subject.id)
        .join(Topic, Topic.chapter_id == Chapter.id)
        .join(Question, Question.topic_id == Topic.id)
        .join(UserAttempt, UserAttempt.question_id == Question.id)
        .scalar()
        or 0
    )
    attempted_chapters_count = (
        db.query(func.count(func.distinct(Chapter.id)))
        .join(Topic, Topic.chapter_id == Chapter.id)
        .join(Question, Question.topic_id == Topic.id)
        .join(UserAttempt, UserAttempt.question_id == Question.id)
        .scalar()
        or 0
    )
    attempted_topics_count = (
        db.query(func.count(func.distinct(Topic.id)))
        .join(Question, Question.topic_id == Topic.id)
        .join(UserAttempt, UserAttempt.question_id == Question.id)
        .scalar()
        or 0
    )

    return StatsResponse(
        total_questions=total_questions,
        total_attempted=total_attempted,
        total_correct=correct_count,
        total_wrong=total_wrong,
        unattempted_questions=unattempted_questions,
        marked_for_review_count=marked_for_review_count,
        attempted_subjects_count=attempted_subjects_count,
        attempted_chapters_count=attempted_chapters_count,
        attempted_topics_count=attempted_topics_count,
        accuracy_percentage=overall_accuracy,
        topic_wise_accuracy=topic_wise,
        difficulty_wise_accuracy=difficulty_wise,
        weak_topics=weak_topics,
    )
