"""Topic API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Chapter, Topic
from app.schemas.taxonomy import TopicCreate, TopicRead

router = APIRouter(prefix="/topics", tags=["topics"])


@router.post("", response_model=TopicRead, status_code=status.HTTP_201_CREATED)
def create_topic(payload: TopicCreate, db: Session = Depends(get_db)) -> Topic:
    if not db.query(Chapter).filter(Chapter.id == payload.chapter_id).first():
        raise HTTPException(status_code=404, detail="Chapter not found.")
    existing = (
        db.query(Topic)
        .filter(Topic.chapter_id == payload.chapter_id, Topic.name == payload.name.strip())
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Topic already exists in this chapter.")
    topic = Topic(chapter_id=payload.chapter_id, name=payload.name.strip())
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.get("", response_model=list[TopicRead])
def list_topics(chapter_id: int = Query(...), db: Session = Depends(get_db)) -> list[Topic]:
    return (
        db.query(Topic)
        .filter(Topic.chapter_id == chapter_id)
        .order_by(Topic.name.asc())
        .all()
    )

