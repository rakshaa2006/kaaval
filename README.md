# Kaaval

Kaaval is a local synthetic demo with a React/Vite frontend and a FastAPI
backend. The current backend MVP supports invoice tasks, deterministic Task
Passports, session action enforcement, incidents, and audit events. It does not
connect to external services or perform real email or destructive actions.

## Run locally

Start the backend in one terminal:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

Start the frontend in a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open <http://localhost:5173>. Configure the browser API URL in the ignored
`frontend/.env.local` file:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

Use **Open Demo** to sign in. The backend must be seeded first; its local demo
owner is `owner@example.test`. API documentation is at
<http://localhost:8000/docs>.

Frontend CI runs `npm ci`, TypeScript checking, and a production build. For
backend tests, run `pytest` from `backend` with the project requirements
installed.