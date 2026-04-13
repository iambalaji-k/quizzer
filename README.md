# CA Final Quiz App

Full-stack quiz application for CA Final students.

## Tech Stack

- Backend: FastAPI, SQLAlchemy, SQLite (PostgreSQL-ready via `DATABASE_URL`)
- Frontend: Next.js (App Router), React, Tailwind CSS
- Charts: Recharts

## Project Structure

```text
backend/
  app/
    api/
    core/
    db/
    models/
    schemas/
    services/
  data/
    sample_questions.csv
    sample_questions.json
    questions_import_schema.json
  requirements.txt
frontend/
  src/
    app/
    components/
    lib/
```

## Backend Features

- Hierarchical relational model: Subject -> Chapter -> Topic -> Question -> Options
- Difficulty enum: `Easy`, `Medium`, `Hard`
- Attempt tracking with correctness and mark-for-review flag
- REST endpoints:
  - `POST /subjects`, `GET /subjects`
  - `POST /chapters`, `GET /chapters?subject_id=`
  - `POST /topics`, `GET /topics?chapter_id=`
  - `POST /questions`, `GET /questions`
  - `PUT /questions/{question_id}`, `DELETE /questions/{question_id}`
  - `POST /attempt`
  - `GET /stats`
  - `GET /attempts` (for review screen support)
  - `POST /import/csv`, `POST /import/json`
  - `POST /import/validate/csv`, `POST /import/validate/json`
- Business logic:
  - Randomized question selection
  - Strict hierarchy filtering by selected subject/chapter/topic
  - Attempted/unattempted filtering
  - Retry wrong questions filtering
  - Dynamic analytics (overall, topic-wise, difficulty-wise, weak topics)
- CSV/JSON bulk import with:
  - Validation
  - Auto-create subject/chapter/topic
  - Failed row logging (`backend/logs/csv_import_failures.log` and `backend/logs/json_import_failures.log`)

## Frontend Features

- `/dashboard`: stats cards + Recharts analytics (accuracy, correct/wrong, unattempted, coverage, marked-for-review) with weak areas by subject/chapter/topic
- `/quiz`: hierarchy selection, difficulty filter, attempted/unattempted filter, retry wrong, choose `All` or specific question count (up to available), one-question flow, immediate feedback, end-of-quiz summary, retake all/wrong-only
- `/manager`: question manager UI for edit/delete without Swagger
- `/review`: attempted questions with selected vs correct answers and explanations
- `/validator`: validate CSV/JSON before upload and inspect detailed errors in the frontend
- `/import`: CSV/JSON upload with success/failure summary
- Responsive Tailwind UI with difficulty color coding

## Run Instructions

### Quick Start (Single File)

```powershell
cd D:\Quiz
powershell -ExecutionPolicy Bypass -File .\start_app.ps1
```

This starts backend + frontend in separate terminals and opens `http://localhost:3000`.

### 1. Backend

```bash
cd backend
..\venv\Scripts\python.exe -m pip install -r requirements.txt
..\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend health check:

```bash
curl http://localhost:8000/health
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

- Frontend: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`

## Environment Variables

Backend (`backend/.env.example`):

- `APP_NAME`
- `APP_VERSION`
- `DATABASE_URL` (switch to PostgreSQL later, e.g. `postgresql+psycopg://...`)
- `CORS_ORIGINS`

Frontend (`frontend/.env.local.example`):

- `NEXT_PUBLIC_API_BASE_URL`

## Sample CSV

Use: `backend/data/sample_questions.csv`

Expected headers:

```text
subject,chapter,topic,difficulty,question,option1,option2,option3,option4,answer,explanation
```

## Sample JSON + Required Schema

Use:

- Sample payload: `backend/data/sample_questions.json`
- JSON schema: `backend/data/questions_import_schema.json`

Expected JSON root format:

```json
{
  "questions": [
    {
      "subject": "Direct Tax Laws",
      "chapter": "Capital Gains",
      "topic": "Exemptions",
      "difficulty": "Easy",
      "question": "Question text",
      "options": ["A", "B", "C", "D"],
      "answer": 1,
      "explanation": "Explanation text"
    }
  ]
}
```
