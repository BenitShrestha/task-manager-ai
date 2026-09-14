# AI-Powered Task Manager API

A multi-user REST API for task management with an AI-powered feature that converts free-text
descriptions of a person's day or week into structured, saved tasks via an LLM call. Built with
production-grade patterns: JWT auth, ownership-scoped queries, retry/validation logic around the
AI call, and a containerized deployment, rather than as a toy CRUD demo.

## Live Demos

- **Backend API Docs (Swagger UI):** https://task-manager-ai-production.up.railway.app/docs
- **Frontend UI (Streamlit):** https://streamlit-frontend-production-e9e3.up.railway.app/

## Features

- JWT-based authentication (register/login) with bcrypt password hashing
- Full task CRUD, strictly scoped to the authenticated user (`owner_id` filtering on every query)
- `POST /tasks/generate` — free text in, structured tasks out via Gemini, with:
  - Input validation (length limits, empty-string rejection)
  - Retry with exponential backoff on API timeout/failure
  - Strict JSON-schema validation of the LLM response before it ever touches the database
  - Graceful `422` on malformed output instead of a silent bad save
- Rate limiting on the AI endpoint specifically (cost-per-call protection)
- Filtering, sorting, and pagination on task listing (`status`, `priority`, `sort`, `skip`, `limit`)
- Streamlit frontend consuming the API end-to-end (auth, CRUD, AI generation)
- pytest suite covering auth, CRUD, ownership isolation, and AI failure modes (LLM mocked, no real API calls in CI)

## Tech Stack

**Backend**
- FastAPI
- PostgreSQL (hosted on [Neon](https://neon.tech))
- SQLAlchemy 2.0 (typed `Mapped`/`mapped_column` style)
- Alembic (migrations)
- JWT auth via `python-jose` + `passlib`/bcrypt
- Google Gemini API (LLM integration)
- `slowapi` (rate limiting)
- pytest + `httpx` TestClient

**Frontend**
- Streamlit
- `requests`

**Infrastructure**
- Docker / Docker Compose
- Railway (backend + frontend deployed as separate services from one monorepo)
- `uv` (Python dependency and virtual environment management)

## Getting Started / Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Configure environment variables

Copy the example env files and fill in real values:

```bash
cp .env.example .env
cp streamlit_app/.env.example streamlit_app/.env
```

`.env` (backend root) requires:

```
DATABASE_URL=<your Neon connection string>
JWT_SECRET=<generate via: python -c "import secrets; print(secrets.token_hex(32))">
GEMINI_API_KEY=<your Gemini API key>
TEST_DATABASE_URL=<a second Neon connection string, for running tests>
```

`streamlit_app/.env` requires:

```
API_BASE_URL=http://localhost:8000
```

### 3. Backend setup

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

API is live at `http://localhost:8000`, interactive docs at `http://localhost:8000/docs`.

### 4. Frontend setup

```bash
cd streamlit_app
uv sync
```

### 5. Run both services locally

In one terminal:

```bash
uv run uvicorn app.main:app --reload
```

In a second terminal:

```bash
cd streamlit_app
uv run streamlit run app.py
```

Frontend is available at `http://localhost:8501` and talks to the backend at `http://localhost:8000`.

### Optional: run via Docker

```bash
docker-compose up --build
```

### Running tests

```bash
uv run pytest -v
```

Tests run against `TEST_DATABASE_URL` (a separate database) and mock all LLM calls — no real API
credits are spent and your primary database is never touched.