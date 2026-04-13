"""Question API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models import Chapter, DifficultyLevel, Option, Question, Topic
from app.schemas.question import QuestionCreate, QuestionRead, QuestionUpdate
from app.services.question_service import count_questions, fetch_questions

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)) -> Question:
    if not db.query(Topic).filter(Topic.id == payload.topic_id).first():
        raise HTTPException(status_code=404, detail="Topic not found.")

    question = Question(
        topic_id=payload.topic_id,
        question_text=payload.question_text.strip(),
        difficulty=payload.difficulty,
        explanation=payload.explanation.strip(),
    )
    db.add(question)
    db.flush()

    for option_payload in payload.options:
        option = Option(
            question_id=question.id,
            option_text=option_payload.option_text.strip(),
            is_correct=option_payload.is_correct,
        )
        db.add(option)

    db.commit()
    db.refresh(question)
    return question


@router.get("", response_model=list[QuestionRead])
def get_questions(
    subject_id: int | None = Query(default=None),
    chapter_id: int | None = Query(default=None),
    topic_id: int | None = Query(default=None),
    difficulty: DifficultyLevel | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    randomize: bool = Query(default=True),
    attempted_only: bool = Query(default=False),
    unattempted_only: bool = Query(default=False),
    retry_wrong: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> list[Question]:
    if attempted_only and unattempted_only:
        raise HTTPException(status_code=400, detail="attempted_only and unattempted_only cannot both be true.")

    questions = fetch_questions(
        db=db,
        subject_id=subject_id,
        chapter_id=chapter_id,
        topic_id=topic_id,
        difficulty=difficulty,
        limit=limit,
        randomize=randomize,
        attempted_only=attempted_only,
        unattempted_only=unattempted_only,
        retry_wrong=retry_wrong,
    )

    if not questions:
        return []

    question_ids = [question.id for question in questions]
    hydrated = (
        db.query(Question)
        .options(
            joinedload(Question.options),
            joinedload(Question.topic).joinedload(Topic.chapter).joinedload(Chapter.subject),
        )
        .filter(Question.id.in_(question_ids))
        .all()
    )

    # Preserve randomized order.
    hydrated_by_id = {question.id: question for question in hydrated}
    return [hydrated_by_id[question_id] for question_id in question_ids if question_id in hydrated_by_id]


@router.get("/count")
def get_questions_count(
    subject_id: int | None = Query(default=None),
    chapter_id: int | None = Query(default=None),
    topic_id: int | None = Query(default=None),
    difficulty: DifficultyLevel | None = Query(default=None),
    attempted_only: bool = Query(default=False),
    unattempted_only: bool = Query(default=False),
    retry_wrong: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    if attempted_only and unattempted_only:
        raise HTTPException(status_code=400, detail="attempted_only and unattempted_only cannot both be true.")

    total = count_questions(
        db=db,
        subject_id=subject_id,
        chapter_id=chapter_id,
        topic_id=topic_id,
        difficulty=difficulty,
        attempted_only=attempted_only,
        unattempted_only=unattempted_only,
        retry_wrong=retry_wrong,
    )
    return {"total": total}


@router.put("/{question_id}", response_model=QuestionRead)
def update_question(question_id: int, payload: QuestionUpdate, db: Session = Depends(get_db)) -> Question:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")
    if not db.query(Topic).filter(Topic.id == payload.topic_id).first():
        raise HTTPException(status_code=404, detail="Topic not found.")

    question.topic_id = payload.topic_id
    question.question_text = payload.question_text.strip()
    question.difficulty = payload.difficulty
    question.explanation = payload.explanation.strip()

    db.query(Option).filter(Option.question_id == question.id).delete(synchronize_session=False)
    for option_payload in payload.options:
        db.add(
            Option(
                question_id=question.id,
                option_text=option_payload.option_text.strip(),
                is_correct=option_payload.is_correct,
            )
        )

    db.commit()
    db.refresh(question)
    return question


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_question(question_id: int, db: Session = Depends(get_db)) -> Response:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")
    db.delete(question)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
