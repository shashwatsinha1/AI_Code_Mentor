
# AI Code Mentor — AI-Powered Coding Environment

AI Code Mentor is a full-stack AI-assisted coding environment
designed to combine code editing, code execution, debugging,
complexity analysis, and AI-based programming assistance in one
workspace.

The system separates three major responsibilities:

    Code Editing
          ↓
    Code Execution
          ↓
    AI Analysis

The frontend provides the interactive coding workspace,
while the FastAPI backend acts as the orchestration layer
between the frontend, database, AI provider, and Judge0.

## Why I Built This

Most coding platforms provide either an editor/compiler
or an AI assistant.

I wanted to understand how these systems could be combined
into a single developer workflow.

The project was therefore designed around four questions:

- How should code drafts be persisted?
- How should untrusted code be executed safely?
- How should AI functionality be exposed through APIs?
- How should AI reasoning be separated from actual execution?

This led to the following architecture:

Editor
   ↓
Backend
   ├── Authentication
   ├── Draft Management
   ├── AI Analysis
   └── Code Execution
          ↓
       Judge0

       
The important architectural distinction is:

AI prediction != actual program execution

The LLM can reason about whether a program appears
correct, but it is not the source of truth for runtime
behavior.

Judge0 therefore acts as the execution layer, while
the AI provider acts as the reasoning layer.

The important architectural distinction is:

AI prediction != actual program execution

The LLM can reason about whether a program appears
correct, but it is not the source of truth for runtime
behavior.

Judge0 therefore acts as the execution layer, while
the AI provider acts as the reasoning layer.


## AI Mentor Architecture

The AI layer is divided into task-specific operations:

/explain
/hint
/detect-bugs
/complexity

Each operation represents a different developer workflow.

                  AI Mentor
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
    Explain         Hint        Bug Detection
       │              │              │
       └──────────────┼──────────────┘
                      ▼
                 AI Service
                      │
                      ▼
                AI Provider



# Data Layer

The backend uses SQLAlchemy as the ORM layer.

Local development uses SQLite:

sqlite+aiosqlite:///./dev.db

The application also includes PostgreSQL support through
asyncpg.

The database layer is responsible for persistent
application state rather than transient AI responses.



# Data Layer

The backend uses SQLAlchemy as the ORM layer.

Local development uses SQLite:

sqlite+aiosqlite:///./dev.db

The application also includes PostgreSQL support through
asyncpg.

The database layer is responsible for persistent
application state rather than transient AI responses.


# Authentication Flow

Signup
  ↓
Validate request
  ↓
Hash password
  ↓
Store user
  ↓
Login
  ↓
Verify password
  ↓
Generate access token
  ↓
Generate refresh token
  ↓
Authenticated API requests



AI_Code_Mentor/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── services/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── pyproject.toml
│   └── .env.example
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
└── .github/
    └── workflows/
        └── ci.yml



# What This Project Demonstrates

Full-Stack Development
        ↓
React + FastAPI
        ↓
REST API Design
        ↓
Authentication
        ↓
Async Database Access
        ↓
External API Integration
        ↓
Code Execution
        ↓
AI-assisted Code Analysis
        ↓
Error Handling
        ↓
Testing + CI
