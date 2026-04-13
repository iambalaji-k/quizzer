"""Attempt and analytics API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Option, Question, UserAttempt
from app.schemas.attempt import AttemptCreate, AttemptResult, ReviewAttempt, StatsResponse
from app.services.stats_service import compute_stats

router = APIRouter(tags=["attempts"])


@router.post("/attempt", response_model=AttemptResult, status_code=status.HTTP_201_CREATED)
def submit_attempt(payload: AttemptCreate, db: Session = Depends(get_db)) -> AttemptResult:
    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    selected_option = db.query(Option).filter(Option.id == payload.selected_option_id).first()
    if not selected_option or selected_option.question_id != question.id:
        raise HTTPException(status_code=400, detail="Selected option does not belong to the question.")

    correct_option = (
        db.query(Option)
        .filter(Option.question_id == question.id, Option.is_correct.is_(True))
        .first()
    )
    if not correct_option:
        raise HTTPException(status_code=500, detail="Question has no correct option configured.")

    attempt = UserAttempt(
        question_id=question.id,
        selected_option_id=selected_option.id,
        is_correct=(selected_option.id == correct_option.id),
        marked_for_review=payload.marked_for_review,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return AttemptResult(
        attempt_id=attempt.id,
        is_correct=attempt.is_correct,
        correct_option_id=correct_option.id,
        explanation=question.explanation,
    )


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)) -> StatsResponse:
    return compute_stats(db)


@router.get("/attempts", response_model=list[ReviewAttempt])
def list_attempts(
    marked_for_review: bool | None = Query(default=None),
    wrong_only: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> list[ReviewAttempt]:
    query = db.query(UserAttempt).order_by(UserAttempt.timestamp.desc())

    if marked_for_review is not None:
        query = query.filter(UserAttempt.marked_for_review == marked_for_review)
    if wrong_only:
        query = query.filter(UserAttempt.is_correct.is_(False))

    attempts = query.all()
    response: list[ReviewAttempt] = []

    for attempt in attempts:
        question = attempt.question
        if not question:
            continue
        options = question.options
        selected_option = next((opt for opt in options if opt.id == attempt.selected_option_id), None)
        correct_option = next((opt for opt in options if opt.is_correct), None)
        topic = question.topic

        if selected_option is None or correct_option is None or topic is None:
            continue

        response.append(
            ReviewAttempt(
                attempt_id=attempt.id,
                question_id=question.id,
                question_text=question.question_text,
                selected_option_id=selected_option.id,
                selected_option_text=selected_option.option_text,
                correct_option_id=correct_option.id,
                correct_option_text=correct_option.option_text,
                is_correct=attempt.is_correct,
                marked_for_review=attempt.marked_for_review,
                difficulty=question.difficulty,
                explanation=question.explanation,
                topic_id=topic.id,
                topic_name=topic.name,
                timestamp=attempt.timestamp,
            )
        )

    return response

