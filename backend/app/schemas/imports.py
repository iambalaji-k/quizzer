"""Schemas for CSV import operations."""

from __future__ import annotations

from pydantic import BaseModel


class CsvImportResponse(BaseModel):
    total_rows: int
    inserted_questions: int
    failed_rows: int
    failures_log_path: str | None = None


class JsonImportResponse(BaseModel):
    total_rows: int
    inserted_questions: int
    failed_rows: int
    failures_log_path: str | None = None


class ValidationErrorDetail(BaseModel):
    row_number: int | None = None
    error: str
    row_data: dict | list | str | None = None


class ValidationResponse(BaseModel):
    file_type: str
    is_valid: bool
    total_rows: int
    failed_rows: int
    errors: list[ValidationErrorDetail]
