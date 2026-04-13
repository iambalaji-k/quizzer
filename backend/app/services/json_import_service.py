"""JSON import service for bulk question ingestion."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models import DifficultyLevel, Option, Question
from app.schemas.imports import JsonImportResponse, ValidationErrorDetail, ValidationResponse
from app.services.taxonomy_service import get_or_create_chapter, get_or_create_subject, get_or_create_topic

FAILURE_LOG_PATH = Path("logs/json_import_failures.log")


def _parse_difficulty(value: str) -> DifficultyLevel:
    normalized = value.strip().capitalize()
    try:
        return DifficultyLevel(normalized)
    except ValueError as exc:
        raise ValueError(f"Invalid difficulty: {value}") from exc


def _resolve_answer_index(answer: str | int, options: list[str]) -> int:
    if isinstance(answer, int):
        idx = answer - 1
        if 0 <= idx < len(options):
            return idx
    if isinstance(answer, str):
        answer_stripped = answer.strip()
        if answer_stripped.isdigit():
            idx = int(answer_stripped) - 1
            if 0 <= idx < len(options):
                return idx
        for index, option in enumerate(options):
            if option.strip().lower() == answer_stripped.lower():
                return index
    raise ValueError("Answer must be option number (1-4) or exact option text.")


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


def _validate_json_payload(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object.")
    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise ValueError("JSON must contain a 'questions' array.")
    return questions


async def import_questions_from_json(db: Session, file: UploadFile) -> JsonImportResponse:
    """Import a JSON file and persist questions with hierarchy auto-creation."""
    raw = await file.read()
    data = json.loads(raw.decode("utf-8-sig"))
    rows = _validate_json_payload(data)

    failed_rows: list[dict[str, Any]] = []
    inserted_questions = 0
    total_rows = 0

    for row_index, row in enumerate(rows, start=1):
        total_rows += 1
        try:
            if not isinstance(row, dict):
                raise ValueError("Each item in 'questions' must be an object.")

            subject_name = str(row["subject"]).strip()
            chapter_name = str(row["chapter"]).strip()
            topic_name = str(row["topic"]).strip()
            question_text = str(row["question"]).strip()
            explanation = str(row["explanation"]).strip()
            options = row["options"]
            answer = row["answer"]

            if not isinstance(options, list) or len(options) != 4:
                raise ValueError("'options' must be an array with exactly 4 entries.")
            options = [str(option).strip() for option in options]
            if any(not option for option in options):
                raise ValueError("All options must be non-empty.")

            if not all([subject_name, chapter_name, topic_name, question_text, explanation]):
                raise ValueError("Subject/chapter/topic/question/explanation must be non-empty.")

            difficulty = _parse_difficulty(str(row["difficulty"]))
            correct_idx = _resolve_answer_index(answer, options)

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
                    "row_data": row,
                }
            )

    db.commit()
    failures_path = _log_failures(failed_rows)

    return JsonImportResponse(
        total_rows=total_rows,
        inserted_questions=inserted_questions,
        failed_rows=len(failed_rows),
        failures_log_path=failures_path,
    )


def validate_json_data(data: Any) -> ValidationResponse:
    """Validate JSON payload without persisting data."""
    rows = _validate_json_payload(data)
    failed_rows: list[ValidationErrorDetail] = []
    total_rows = 0

    for row_index, row in enumerate(rows, start=1):
        total_rows += 1
        try:
            if not isinstance(row, dict):
                raise ValueError("Each item in 'questions' must be an object.")

            subject_name = str(row["subject"]).strip()
            chapter_name = str(row["chapter"]).strip()
            topic_name = str(row["topic"]).strip()
            question_text = str(row["question"]).strip()
            explanation = str(row["explanation"]).strip()
            options = row["options"]
            answer = row["answer"]

            if not isinstance(options, list) or len(options) != 4:
                raise ValueError("'options' must be an array with exactly 4 entries.")
            options = [str(option).strip() for option in options]
            if any(not option for option in options):
                raise ValueError("All options must be non-empty.")
            if not all([subject_name, chapter_name, topic_name, question_text, explanation]):
                raise ValueError("Subject/chapter/topic/question/explanation must be non-empty.")

            _parse_difficulty(str(row["difficulty"]))
            _resolve_answer_index(answer, options)
        except Exception as exc:
            failed_rows.append(
                ValidationErrorDetail(
                    row_number=row_index,
                    error=str(exc),
                    row_data=row if isinstance(row, dict) else str(row),
                )
            )

    return ValidationResponse(
        file_type="json",
        is_valid=(len(failed_rows) == 0),
        total_rows=total_rows,
        failed_rows=len(failed_rows),
        errors=failed_rows,
    )


async def validate_json_file(file: UploadFile) -> ValidationResponse:
    """Validate uploaded JSON file without persisting data."""
    raw = await file.read()
    data = json.loads(raw.decode("utf-8-sig"))
    return validate_json_data(data)
