# AI Code Mentor

Phase 3 scaffold for the AI Code Mentor app.

## Stack

- Frontend: React, Vite, Tailwind CSS, Monaco Editor, Chart.js
- Backend: FastAPI, SQLAlchemy async, Alembic
- Data: SQLite locally by default, PostgreSQL/Redis later when deployment is revisited
- Auth: JWT access tokens with rotating refresh tokens

## Run locally

Start the backend:

```bash
cd backend
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Start the frontend in another terminal:

```bash
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

## Backend checks

```bash
cd backend
python -m pip install -e ".[dev]"
ruff check .
pytest
```

## Frontend checks

```bash
cd frontend
npm install
npm run lint
npm run build
```

## Phase 1 Exit Criteria

- Register via `/auth/signup`
- Log in via `/auth/login`
- Rotate refresh tokens via `/auth/refresh`
- Hit protected `/users/me`
- Use the React signup, login, and profile screens
- Run with local backend and frontend dev commands

## Phase 2 Workspace

- Protected workspace: http://localhost:5173/workspace
- Draft API: `GET /drafts/{language}` and `PUT /drafts`
- Execute API: `POST /execute`

Execution uses Judge0 through the backend, keeping untrusted code away from the app server.
Set `JUDGE0_API_URL` if you want to point at a hosted or self-hosted Judge0 instance. The
default is `https://ce.judge0.com`.

Optional Judge0 settings:

- `JUDGE0_AUTH_TOKEN`
- `JUDGE0_RAPIDAPI_KEY`
- `JUDGE0_RAPIDAPI_HOST`
- `JUDGE0_TIMEOUT_SECONDS`

## Phase 3 AI Mentor

- Explain code: `POST /explain`
- Generate staged hints: `POST /hint`
- Detect bugs: `POST /detect-bugs`
- Analyze complexity: `POST /complexity`

Set `OPENAI_API_KEY` to use the OpenAI-backed mentor. Without a key, the backend returns local
heuristic responses so the UI remains usable during development.
