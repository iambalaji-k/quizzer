"""Chapter API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Chapter, Subject
from app.schemas.taxonomy import ChapterCreate, ChapterRead

router = APIRouter(prefix="/chapters", tags=["chapters"])


@router.post("", response_model=ChapterRead, status_code=status.HTTP_201_CREATED)
def create_chapter(payload: ChapterCreate, db: Session = Depends(get_db)) -> Chapter:
    if not db.query(Subject).filter(Subject.id == payload.subject_id).first():
        raise HTTPException(status_code=404, detail="Subject not found.")
    existing = (
        db.query(Chapter)
        .filter(Chapter.subject_id == payload.subject_id, Chapter.name == payload.name.strip())
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Chapter already exists in this subject.")
    chapter = Chapter(subject_id=payload.subject_id, name=payload.name.strip())
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


@router.get("", response_model=list[ChapterRead])
def list_chapters(subject_id: int = Query(...), db: Session = Depends(get_db)) -> list[Chapter]:
    return (
        db.query(Chapter)
        .filter(Chapter.subject_id == subject_id)
        .order_by(Chapter.name.asc())
        .all()
    )

