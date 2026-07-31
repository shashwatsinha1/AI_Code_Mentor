# CodeMentor AI - Build Roadmap for Codex

A phased plan that breaks the full spec into shippable milestones.

---

## 0. Ground Rules Before You Start

- Feed Codex one phase at a time.
- Keep the repo as a monorepo with `/frontend` and `/backend`.
- Use Python 3.11+ and Node 20+.
- Run locally with normal backend/frontend dev commands.
- Do not execute untrusted user code directly on the host.

### Locked Stack

| Layer | Choice |
|---|---|
| Frontend | React + Vite, Tailwind CSS, Monaco Editor, Chart.js |
| Backend | FastAPI (Python), SQLAlchemy async, Alembic |
| DB | SQLite locally now; PostgreSQL/Redis when deployment is revisited |
| Vector DB | Qdrant later |
| LLM | OpenAI API to start, with local fallback responses for development |
| Auth | JWT access + refresh tokens |
| Deploy | GitHub Actions CI first; deployment later when requested |

---

## Phase 1 - Foundation & Auth (Done)

**Goal:** working skeleton app with real login, running locally with dev commands.

Scope:
- Repo scaffold with `/frontend` and `/backend`
- User model, signup/login, JWT access and refresh tokens, password hashing
- Protected route middleware
- Basic user profile page
- CI pipeline for lint/tests

**Exit criteria:** Can register, log in, hit `/users/me`, and see a profile page.

---

## Phase 2 - Coding Workspace (Done)

**Goal:** users can write code in-browser and persist drafts.

Scope:
- Monaco Editor integration for Python, Java, and C++
- Theme toggle
- Debounced auto-save to a `drafts` table
- `/execute` endpoint runs code through Judge0

**Exit criteria:** User can write code in Monaco and have it persist across reloads.

Code execution note:
Do not use `exec()` or `subprocess.run()` on untrusted user code. The app uses Judge0 as the
isolated execution service.

---

## Phase 3 - AI Mentor Core (Current Phase)

**Goal:** the four text-in, text-out AI mentor features that do not require grading logic.

Scope:
- `AIMentorService` in the FastAPI backend
- Prompt templates in separate files
- Code explanation endpoint: `POST /explain`
- Hint endpoint: `POST /hint`
- Bug detection endpoint: `POST /detect-bugs`
- Complexity analysis endpoint: `POST /complexity`
- React workspace side panel with tabs for each mentor feature

**Exit criteria:** Paste code in workspace and get an explanation, staged hint, bug report, or
complexity estimate in the side panel.

---

## Phase 4 - Optimization + Problem Bank

**Goal:** structured problems to practice against, plus code optimization.

Scope:
- `Problem` model with title, difficulty, tags, description, and test cases
- Seed 30-50 DSA problems
- Problem list and detail pages in React
- Code optimization endpoint using the AI mentor service

**Exit criteria:** Browse problems, open one, and ask for optimization guidance.

Grading against test cases should wait until a safe execution worker is available.

---

## Phase 5 - Progress Tracking & Roadmap

**Goal:** turn solved problems into a personalized plan.

Scope:
- Track attempts and solves per user per topic
- Weak-topic detection by tag pass rate
- Recommended problems and daily goal generator
- Progress dashboard with Chart.js

**Exit criteria:** Dashboard shows solved count, weak topics, and recommended next problems.

---

## Phase 6 - Interview Simulator

**Goal:** text-based mock interview flow.

Scope:
- Interview session model
- Question bank across DSA/OOP/DBMS/OS/CN
- LLM-driven follow-up questioning
- Post-interview scorecard
- React interview page with chat-style transcript

**Exit criteria:** User completes a mock interview and receives a scored summary.

---

## Phase 7 - Vector Search / RAG Layer

**Goal:** ground AI answers in real problem context and past sessions.

Scope:
- Qdrant setup
- Embedding pipeline for problems, submissions, and interview transcripts
- Retrieval-augmented mentor prompts
- LeetCode Companion endpoint and page

**Exit criteria:** Pasting a problem description surfaces similar problems and contextual hints.

---

## Phase 8 - Contest Analysis

Scope:
- Import or paste contest submissions
- Aggregate mistakes across a contest
- Recommend topics to revise and similar problems

---

## Phase 9 - Stretch Features

Pick one at a time:
- Resume-based interview
- Voice interview
- Whiteboard mode
- Google OAuth

---

## Suggested Order If Time-Constrained

1. Phases 1-3: auth, workspace, core AI mentor
2. Phase 6: interview simulator
3. Phases 4-5: problem bank and progress
4. Phase 7: RAG
5. Stretch features
