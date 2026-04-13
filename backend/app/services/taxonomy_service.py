"""Services for taxonomy hierarchy operations."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Chapter, Subject, Topic


def get_or_create_subject(db: Session, name: str) -> Subject:
    subject = db.query(Subject).filter(Subject.name == name.strip()).first()
    if subject:
        return subject
    subject = Subject(name=name.strip())
    db.add(subject)
    db.flush()
    return subject


def get_or_create_chapter(db: Session, subject_id: int, name: str) -> Chapter:
    chapter = (
        db.query(Chapter)
        .filter(Chapter.subject_id == subject_id, Chapter.name == name.strip())
        .first()
    )
    if chapter:
        return chapter
    chapter = Chapter(subject_id=subject_id, name=name.strip())
    db.add(chapter)
    db.flush()
    return chapter


def get_or_create_topic(db: Session, chapter_id: int, name: str) -> Topic:
    topic = db.query(Topic).filter(Topic.chapter_id == chapter_id, Topic.name == name.strip()).first()
    if topic:
        return topic
    topic = Topic(chapter_id=chapter_id, name=name.strip())
    db.add(topic)
    db.flush()
    return topic

