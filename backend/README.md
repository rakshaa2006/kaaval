# Kaaval Backend Skeleton

Minimal FastAPI backend scaffold using Pydantic, SQLAlchemy, and SQLite for local development. All development data must be synthetic. This scaffold does not implement product workflows, external integrations, or a frontend.

## Prerequisites

- Python 3.12+
- pip

## Local Setup

```bash
# Run these commands from the backend directory.

# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment variables
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux

# 4. Run the application
uvicorn app.main:app --reload --port 8000
```

The API will be available at http://localhost:8000

- Liveness: http://localhost:8000/api/health
- Readiness (checks SQLite connectivity): http://localhost:8000/api/ready
- API docs: http://localhost:8000/docs

## Running Tests

```bash
pytest
```

## Environment Variables

See `.env.example` for all supported variables with descriptions.

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `SYNTHETIC_DEMO` | Runtime environment |
| `DATABASE_URL` | `sqlite:///./kaaval.db` | Database connection URL |

## Project Structure

```
backend/
  app/
    main.py          — FastAPI application factory
    config.py        — Pydantic settings
    api/             — Health and readiness routes
    auth/            — Reserved for future authentication code
    models/          — SQLAlchemy model definitions
    schemas/         — Pydantic schemas
    db/              — SQLite engine and session factory
    services/        — Reserved for future service code
    policy/          — Reserved for future policy code
    tools/           — Reserved for future tool adapters
    audit/           — Reserved for future audit code
    integrations/    — Reserved for future integration adapters
    attack_lab/      — Reserved for future simulation code
  tests/             — pytest health/readiness tests
```

No email, file deletion, customer data, messaging credentials, or external LLM integration is configured or implemented.
