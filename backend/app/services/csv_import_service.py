"""CSV import service for bulk question ingestion."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models import DifficultyLevel, Option, Question
from app.schemas.imports import CsvImportResponse, ValidationErrorDetail, ValidationResponse
from app.services.taxonomy_service import get_or_create_chapter, get_or_create_subject, get_or_create_topic

REQUIRED_COLUMNS = [
    "subject",
    "chapter",
    "topic",
    "difficulty",
    "question",
    "option1",
    "option2",
    "option3",
    "option4",
    "answer",
    "explanation",
]

FAILURE_LOG_PATH = Path("logs/csv_import_failures.log")


def _parse_difficulty(value: str) -> DifficultyLevel:
    normalized = value.strip().capitalize()
    try:
        return DifficultyLevel(normalized)
    except ValueError as exc:
        raise ValueError(f"Invalid difficulty: {value}") from exc


def _resolve_answer_index(answer: str, options: list[str]) -> int:
    answer_stripped = answer.strip()
    if answer_stripped.isdigit():
        idx = int(answer_stripped) - 1
        if 0 <= idx < len(options):
            return idx
    for index, option in enumerate(options):
        if option.strip().lower() == answer_stripped.lower():
            return index
    raise ValueError("Answer must be option number (1-4) or exact option text.")


def _validate_headers(headers: list[str] | None) -> None:
    if headers is None:
        raise ValueError("CSV is empty.")
    missing = [col for col in REQUIRED_COLUMNS if col not in headers]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def _log_failures(failed_rows: list[dict[str, Any]]) -> str | None:
    if not failed_rows:
        return None
    FAILURE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with FAILURE_LOG_PATH.open("w", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["row_number", "error", "row_data"])
        writer.writeheader()
        for row in failed_rows:
            writer.writerow(row)
    return str(FAILURE_LOG_PATH)


async def import_questions_from_csv(db: Session, file: UploadFile) -> CsvImportResponse:
    """Import a CSV file and persist questions with hierarchy auto-creation."""
    raw = await file.read()
    text_stream = StringIO(raw.decode("utf-8-sig"))
    reader = csv.DictReader(text_stream)
    _validate_headers(reader.fieldnames)

    failed_rows: list[dict[str, Any]] = []
    inserted_questions = 0
    total_rows = 0

    for row_index, row in enumerate(reader, start=2):
        total_rows += 1
        try:
            subject_name = row["subject"].strip()
            chapter_name = row["chapter"].strip()
            topic_name = row["topic"].strip()
            question_text = row["question"].strip()
            explanation = row["explanation"].strip()
            options = [row[f"option{i}"].strip() for i in range(1, 5)]

            if not all([subject_name, chapter_name, topic_name, question_text, explanation]):
                raise ValueError("Subject/chapter/topic/question/explanation must be non-empty.")
            if any(not option for option in options):
                raise ValueError("All options must be non-empty.")

            difficulty = _parse_difficulty(row["difficulty"])
            correct_idx = _resolve_answer_index(row["answer"], options)

            subject = get_or_create_subject(db, subject_name)
            chapter = get_or_create_chapter(db, subject.id, chapter_name)
            topic = get_or_create_topic(db, chapter.id, topic_name)

            question = Question(
                topic_id=topic.id,
                question_text=question_text,
                difficulty=difficulty,
                explanation=explanation,
            )
            db.add(question)
            db.flush()

            for idx, option_text in enumerate(options):
                db.add(
                    Option(
                        question_id=question.id,
                        option_text=option_text,
                        is_correct=(idx == correct_idx),
                    )
                )

            inserted_questions += 1
        except Exception as exc:
            failed_rows.append(
                {
                    "row_number": row_index,
                    "error": str(exc),
                    "row_data": dict(row),
                }
            )

    db.commit()
    failures_path = _log_failures(failed_rows)

    return CsvImportResponse(
        total_rows=total_rows,
        inserted_questions=inserted_questions,
        failed_rows=len(failed_rows),
        failures_log_path=failures_path,
    )


def validate_csv_text(text: str) -> ValidationResponse:
    """Validate CSV contents without persisting data."""
    text_stream = StringIO(text)
    reader = csv.DictReader(text_stream)
    failed_rows: list[ValidationErrorDetail] = []

    try:
        _validate_headers(reader.fieldnames)
    except Exception as exc:
        return ValidationResponse(
            file_type="csv",
            is_valid=False,
            total_rows=0,
            failed_rows=1,
            errors=[ValidationErrorDetail(row_number=1, error=str(exc), row_data=reader.fieldnames or "")],
        )

    total_rows = 0

    for row_index, row in enumerate(reader, start=2):
        total_rows += 1
        try:
            subject_name = row["subject"].strip()
            chapter_name = row["chapter"].strip()
            topic_name = row["topic"].strip()
            question_text = row["question"].strip()
            explanation = row["explanation"].strip()
            options = [row[f"option{i}"].strip() for i in range(1, 5)]

            if not all([subject_name, chapter_name, topic_name, question_text, explanation]):
                raise ValueError("Subject/chapter/topic/question/explanation must be non-empty.")
            if any(not option for option in options):
                raise ValueError("All options must be non-empty.")

            _parse_difficulty(row["difficulty"])
            _resolve_answer_index(row["answer"], options)
        except Exception as exc:
            failed_rows.append(
                ValidationErrorDetail(
                    row_number=row_index,
                    error=str(exc),
                    row_data=dict(row),
                )
            )

    return ValidationResponse(
        file_type="csv",
        is_valid=(len(failed_rows) == 0),
        total_rows=total_rows,
        failed_rows=len(failed_rows),
        errors=failed_rows,
    )


async def validate_csv_file(file: UploadFile) -> ValidationResponse:
    """Validate uploaded CSV file without persisting data."""
    raw = await file.read()
    return validate_csv_text(raw.decode("utf-8-sig"))
