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

# 4. Create local schema and synthetic demo data
python -m app.seed

# 5. Run the application
uvicorn app.main:app --reload --port 8000
```

The API will be available at http://localhost:8000

- Liveness: http://localhost:8000/api/health
- Readiness (checks SQLite connectivity): http://localhost:8000/api/ready
- Demo authentication: `POST /api/auth/demo-login` (synthetic mode only)
- Password authentication: `POST /api/auth/login`
- Current user: `GET /api/auth/me`
- Logout: `POST /api/auth/logout`
- Tasks: `POST /api/tasks`, `GET /api/tasks/{task_id}`
- Task Passports: `POST /api/tasks/{task_id}/passport/generate`,
  `GET /api/tasks/{task_id}/passport`,
  `POST /api/tasks/{task_id}/passport/activate`, and
  `POST /api/tasks/{task_id}/passport/regenerate`
- Action enforcement: `POST /api/sessions/{session_id}/actions`
- Incident review: `GET /api/incidents`,
  `GET /api/incidents/{incident_id}`,
  `POST /api/incidents/{incident_id}/acknowledge`, and
  `POST /api/incidents/{incident_id}/resolve`
- API docs: http://localhost:8000/docs

## Running Tests

```bash
pytest
```

The test suite uses an isolated in-memory SQLite database with foreign-key
enforcement enabled. The application initializes SQLAlchemy tables on startup.

## Synthetic Demo Credentials

The local seed command creates `owner@example.test` with the demo-only password
`kaaval-demo-only`. The seed command is restricted to `SYNTHETIC_DEMO` with
SQLite; the database stores only a salted scrypt hash, never the plaintext
password. Do not use this demo password outside local synthetic development.

Login responses set an HttpOnly `kaaval_session` cookie. The database stores
only a SHA-256 hash of the opaque session token; sessions expire after the
configured lifetime and logout revokes the active session. Bearer tokens are
also accepted for API clients.

## Environment Variables

See `.env.example` for all supported variables with descriptions.

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `SYNTHETIC_DEMO` | Runtime environment |
| `DATABASE_URL` | `sqlite:///./kaaval.db` | Database connection URL |
| `SESSION_EXPIRE_HOURS` | `8` | Browser session lifetime |
| `PASSPORT_EXPIRE_HOURS` | `24` | Generated Task Passport lifetime |

## Project Structure

```
backend/
  app/
    main.py          — FastAPI application factory
    config.py        — Pydantic settings
    api/             — Health, readiness, and authentication routes
    auth/            — Password hashing and browser-session helpers
    models/          — SQLAlchemy model definitions
    schemas/         — Pydantic schemas
    db/              — SQLite engine and session factory
    services/        — Reserved for future service code
    policy/          — Reserved for future policy code
    tools/           — Internal mock tool registry; no public tool endpoints
    audit/           — Append-only audit event persistence
    integrations/    — Reserved for future integration adapters
    attack_lab/      — Reserved for future simulation code
  tests/             — pytest health, schema, relationship, and scope tests
```

The internal mock tool registry exposes lookup and execution through
`app.tools`, but no tool is callable through an HTTP endpoint. `read_invoice`
reads only the synthetic invoice fixtures; `send_email` and `delete_backup`
return simulated results without network or filesystem side effects.

Protected actions must use the enforcement gateway. It persists an action and
policy decision before executing an allowed mock tool. For the current MVP,
only an active session with a valid active Passport may perform an allowed
synthetic invoice read; email and backup deletion are never executed.

The gateway inspects synthetic action context, stores only masked findings,
and quarantines sessions for severe unsafe actions. Quarantine incidents and
mock notification intents are persisted transactionally; resolving an incident
does not reactivate its session.

No real email, file deletion, customer data, messaging credentials, or external
LLM integration is configured or implemented.
