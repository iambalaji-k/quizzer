"""CSV import API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.imports import CsvImportResponse, JsonImportResponse, ValidationResponse
from app.services.csv_import_service import import_questions_from_csv, validate_csv_file
from app.services.json_import_service import import_questions_from_json, validate_json_file

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/csv", response_model=CsvImportResponse)
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)) -> CsvImportResponse:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    return await import_questions_from_csv(db, file)


@router.post("/json", response_model=JsonImportResponse)
async def import_json(file: UploadFile = File(...), db: Session = Depends(get_db)) -> JsonImportResponse:
    if not file.filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are supported.")
    try:
        return await import_questions_from_json(db, file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/validate/csv", response_model=ValidationResponse)
async def validate_csv(file: UploadFile = File(...)) -> ValidationResponse:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    try:
        return await validate_csv_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/validate/json", response_model=ValidationResponse)
async def validate_json(file: UploadFile = File(...)) -> ValidationResponse:
    if not file.filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are supported.")
    try:
        return await validate_json_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
