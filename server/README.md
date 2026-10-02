# DEVS Investiture — Backend API

FastAPI backend for the **DEVS Investiture Event Registration & Attendance Platform**.

> **Location:** `server/`  
> **Language:** Python 3.12  
> **Package manager:** [uv](https://docs.astral.sh/uv/)

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Folder Responsibilities](#folder-responsibilities)
- [Architecture & Layering](#architecture--layering)
- [Authentication & Authorization](#authentication--authorization)
- [Database & Migrations](#database--migrations)
- [Rate Limiting](#rate-limiting)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)
- [Development Commands](#development-commands)
- [Code Quality](#code-quality)
- [Git & Pull Requests](#git--pull-requests)
- [Backend Definition of Done](#backend-definition-of-done)

---

## Overview

The backend is the **authoritative layer** of the platform. It enforces identity, roles, registration uniqueness, QR validity, attendance state and event timing. The frontend is a thin client and never a security boundary.

```text
Client
  ↓
FastAPI API (routers)
  ↓
Services (use cases)
  ↓
SQLAlchemy / PostgreSQL
```

The backend serves two primary experiences:

### Student

```text
Google Login → Registration → Entry Ticket → Exit Ticket when enabled
```

### Checker / Admin

```text
Google Login → Scanner → QR Result → ID Verification → Attendance Decision → Dashboard
```

---

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | HTTP API framework |
| Pydantic v2 | Request/response validation |
| pydantic-settings | Environment-based configuration |
| SQLAlchemy 2.0 | ORM / database access |
| Alembic | Schema migrations |
| PostgreSQL | Primary relational database |
| psycopg 3 | PostgreSQL driver |
| slowapi | Rate limiting |
| python-jose | JWT creation and verification |
| uvicorn | ASGI server |
| uv | Package and dependency management |

---

## Requirements

Install:

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — package installer and resolver
- Docker + Docker Compose — for PostgreSQL (or a local PostgreSQL install)
- Redis — optional, only when rate-limit storage / Celery is enabled

Check versions:

```bash
python --version
uv --version
docker --version
```

---

## Getting Started

### 1. Start PostgreSQL

From the repository root:

```bash
docker compose up -d
```

This starts the `postgres` service (default credentials match `server/.env.example`).

### 2. Set up environment variables

```bash
cd server
cp .env.example .env
```

Edit `.env` and update the key variables:

```env
DATABASE_URI=postgresql+psycopg://postgres:postgres@localhost:5432/devs_investiture

# Security (IMPORTANT: Change in production!)
SECRET_KEY=your-secret-key-here-change-in-production

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Install dependencies

```bash
uv sync
```

This creates the virtual environment and installs everything from `pyproject.toml` and `uv.lock`.

### 4. Run migrations

```bash
uv run alembic upgrade head
```

### 5. Run the application

```bash
uv run main.py
```

The app also auto-creates missing tables at startup via `init_db()`.

The development server runs at:

```text
http://localhost:8000
```

Docs:

```text
http://localhost:8000/api/docs
```

---

# Project Structure

```text
server/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── health.py            # health check endpoint
│   │       │   └── ...                  # auth, users, attendance, etc.
│   │       └── api.py                   # aggregates routers under /api/v1
│   │
│   ├── core/
│   │   ├── config.py                    # application settings (pydantic-settings)
│   │   └── rate_limiter.py              # slowapi rate limiter
│   │
│   ├── db/
│   │   └── session.py                   # engine, session factory, Base, init_db
│   │
│   ├── dependancies/
│   │   └── auth.py                      # FastAPI auth dependencies
│   │
│   ├── models/
│   │   └── users.py                     # SQLAlchemy ORM models
│   │
│   ├── schemas/
│   │   └── auth.py                      # Pydantic schemas
│   │
│   └── services/
│       └── auth.py                      # business logic / use cases
│
├── alembic/
│   ├── env.py                           # Alembic environment config
│   └── versions/                        # generated migration scripts
│
├── backup/
│   ├── backup.sh                        # backup job entrypoint
│   └── Dockerfile                       # containerized backup job
│
├── main.py                              # application entry point
├── alembic.ini                          # Alembic configuration
├── pyproject.toml                       # dependencies and project config
├── uv.lock                              # locked dependency versions
├── .env.example                         # environment template
├── .python-version
├── .gitignore
└── README.md
```

### Structure rules

- Routers contain HTTP concerns only.
- Services contain application use cases.
- Models contain ORM entities.
- Schemas contain Pydantic models for API boundaries.
- Repositories/data access remain separated from services.
- Infrastructure concerns (Google, email, storage) stay in their own layer.

---

# Folder Responsibilities

## `app/api/`

HTTP routers and endpoints.

```text
app/api/v1/api.py
app/api/v1/endpoints/
```

`api.py` aggregates feature routers; all are mounted under the `/api/v1` prefix.

## `app/core/`

Cross-cutting application configuration.

```text
config.py          # Settings loaded from .env via pydantic-settings
rate_limiter.py    # slowapi Limiter instance
```

## `app/db/`

Database engine, session management and the ORM base.

```text
session.py         # engine, SessionLocal, Base, get_db dependency, init_db
```

## `app/models/`

SQLAlchemy ORM models. Models must be imported so they register on `Base.metadata` before migrations or `create_all`.

## `app/schemas/`

Pydantic schemas. These define the API contract — never expose ORM objects directly.

## `app/services/`

Business logic and use-case orchestration. Services do not contain HTTP concerns.

## `app/dependancies/`

Reusable FastAPI dependencies such as authentication and authorization.

## `alembic/`

Alembic migration environment and generated version scripts.

## `backup/`

Containerized database backup job.

---

# Architecture & Layering

The backend follows the layered design from the repository root:

```text
1. API / Router      HTTP concerns, dependencies, response mapping
2. Application       use-case orchestration
3. Domain            entities, enums, business rules and invariants
4. Repository        SQLAlchemy queries and persistence
5. Infrastructure    Google, email, PDF, storage, external integrations
```

### Rules

- Explicit transaction boundaries.
- No hidden commits inside repositories.
- Pydantic models at API boundaries.
- Never expose ORM objects directly.
- Dependency injection for sessions, users, roles and services.
- Structured logging with request/trace IDs.
- Never log tokens, cookies, credentials or unnecessary PII.

---

# Authentication & Authorization

Google OAuth/OIDC is the **only authentication method**.

Accepted domain:

```text
@rajalakshmi.edu.in
```

- The backend rejects non-institutional identities even on direct API calls.
- Google's stable `sub` is the external identity key; email is an attribute, not the sole key.
- Sessions use `Secure`, `HttpOnly`, appropriate `SameSite` cookies.
- No long-lived auth tokens in `localStorage`.
- Authorization is enforced server-side only. Students cannot reach scanner/admin APIs or mutate attendance.

---

# Database & Migrations

## Connection

The database URI comes from `DATABASE_URI`:

```env
DATABASE_URI=postgresql+psycopg://postgres:postgres@localhost:5432/devs_investiture
```

`app/db/session.py` builds the engine with `pool_pre_ping=True`.

## Startup

`init_db()` imports all models and runs `Base.metadata.create_all()` so tables exist on first start.

## Migrations with Alembic

Generate a migration from model changes:

```bash
uv run alembic revision --autogenerate -m "describe the change"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Alembic reads `DATABASE_URI` from the application settings (`alembic/env.py`).

---

# Rate Limiting

Rate limiting uses [slowapi](https://github.com/slowapi/slowapi) configured in `app/core/rate_limiter.py`.

- Default limit: `RATE_LIMIT_PER_MINUTE` per minute per client.
- Storage: `REDIS_URL` when Redis is available.
- Enable/disable via `RATE_LIMIT_ENABLED`.

---

# API Documentation

Once the application is running:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

### Current endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Root health/status check |
| `GET` | `/api/v1/health` | Service health check |

---

# Environment Variables

Create local environment configuration from the example:

```bash
cp .env.example .env
```

Never commit `.env`.

### Key variables

| Variable | Purpose | Example |
|---|---|---|
| `DATABASE_URI` | PostgreSQL connection string | `postgresql+psycopg://postgres:postgres@localhost:5432/devs_investiture` |
| `SECRET_KEY` | JWT signing secret | change in production |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:3000,http://localhost:5173` |
| `REDIS_URL` | Redis connection for rate limiting / Celery | `redis://localhost:6379/0` |
| `RATE_LIMIT_ENABLED` | Toggle rate limiting | `True` |
| `RATE_LIMIT_PER_MINUTE` | Default requests per minute | `60` |
| `DEBUG` | Reload/debug mode | `True` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FORMAT` | Logging format (`json`/text) | `json` |

The Docker Compose PostgreSQL container is configured from the root `.env.example` (user `postgres`, password `postgres`, database `devs_investiture`, port `5432`).

---

# Development Commands

```bash
uv sync                                        # install dependencies
uv sync --extra test                           # install with test dependencies (pytest)
uv run pytest                                  # run server pytest test suite
uv run pytest --cov=app --cov-report=term      # run tests with coverage report
uv run main.py                                 # run with auto-reload (DEBUG=True)
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4   # production-ish
uv run alembic upgrade head                    # apply migrations
uv run alembic revision --autogenerate -m "..."   # create a migration
```

`pyproject.toml` and `uv.lock` are the source of truth for dependencies.

---

# Code Quality

### Rules

- Routers contain HTTP concerns only.
- Services contain application use cases.
- Domain rules remain explicit.
- Repositories manage persistence.
- Infrastructure handles external integrations.
- Explicit transaction boundaries.
- Pydantic at API boundaries.
- No direct ORM exposure.
- Dependency injection.
- Structured logging.
- No sensitive credentials/tokens in logs.
- Automated tests for business-critical paths.
- No giant functions, duplicated business rules, magic values, silent exception handling or dead code.

---

# Git & Pull Requests

Follow the repository's fork-based workflow:

```text
Fork
  ↓
Feature branch
  ↓
Implement
  ↓
Test
  ↓
Commit
  ↓
Push to fork
  ↓
Pull Request
  ↓
Review
  ↓
Merge by lead
```

**Do not directly push feature work to the upstream/main branch.**

### Commit format

```text
(scope?): short description
```

Examples:

```text
feat(auth): add Google institutional login
feat(attendance): prevent duplicate QR consumption
refactor(registration): separate registration service
perf(admin): optimize attendance query
docs(server): update backend setup
build(server): update Docker configuration
ops: add production backup job
chore: update gitignore
```

### Dependency changes

Any dependency change must be a dedicated `chore:` commit.

Example:

```text
chore: add sqlalchemy dependency to requirements.txt
```

Do not bundle it with:

```text
feat(database): add SQLAlchemy registration repository
```

The feature implementation must be a separate follow-up commit.

---

# Backend Definition of Done

A backend feature is complete when:

- [ ] Only `@rajalakshmi.edu.in` users can create student sessions.
- [ ] One event registration per student is database-enforced.
- [ ] Registration produces an entry QR and email.
- [ ] Entry QR is opaque, time-bound and one-time-use.
- [ ] Multiple scanners operate concurrently without duplicate acceptance.
- [ ] Present/Absent/Forgery decisions are auditable.
- [ ] Exit QR is locked until the configured window.
- [ ] On-spot registration cannot create duplicates.
- [ ] OD PDF contains the required watermark and is protected from public access.
- [ ] XSS, SQLi, OAuth bypass, privilege escalation and QR race/replay tests pass.
- [ ] Rate limiting and file-upload abuse tests pass.
- [ ] Migrations are versioned with Alembic and run cleanly.
- [ ] No ORM objects are exposed directly at API boundaries.
- [ ] No sensitive credentials/tokens are logged.
- [ ] Docker deployment and PostgreSQL backup/restore are verified.
- [ ] No secrets are committed.
- [ ] PR contains clear implementation and testing information.

---

## Background jobs

Compose starts one Redis broker, the API, and one worker consuming both
`registration_email` and `od_email` queues:

```bash
docker compose up -d
docker compose logs -f worker
```

For a local worker:

```bash
uv run celery -A app.worker.celery_app:celery_app worker -Q registration_email,od_email --loglevel=INFO
```

Registration commits before calling `.delay(registration_id)`, so email
delivery does not delay or fail a successful registration response. The task
contains only the registration ID; the worker reloads the record from
PostgreSQL. Successful results are ignored because no result backend is
configured. Temporary failures retry up to three times with exponential
backoff. After the final retry, Celery marks the task failed and logs the
exception. The OD task is intentionally a logged placeholder.

## Reference Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/) — HTTP API framework.
- [Pydantic Documentation](https://docs.pydantic.dev/) — data validation and schemas.
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/) — ORM and database access.
- [Alembic Documentation](https://alembic.sqlalchemy.org/) — database migrations.
- [PostgreSQL Documentation](https://www.postgresql.org/docs/) — database reference.
- [uv Documentation](https://docs.astral.sh/uv/) — Python package manager.
- [slowapi](https://github.com/slowapi/slowapi) — rate limiting.
