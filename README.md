# FormForge API

FormForge API is the backend service powering **FormForge**, a dynamic form builder with a rule engine and AI-assisted form generation. It manages form schemas, handles user submissions, and exposes data for export and integrations.

Built with **FastAPI** and following **Clean Architecture**, the codebase keeps a clear separation between API, business logic, domain models, and infrastructure.

---

## Features

- **Dynamic forms** — field definitions, validations, and conditional rules stored as JSON and evaluated in the service layer
- **Submissions** — collect, query (with per-field filtering), and export submissions to CSV
- **AI form generation** — turn a plain-text description into a form schema via an OpenAI-compatible provider (Gemini by default)
- **Excel import** — download a template, then upload a filled `.xlsx` to generate a form
- **Authentication** — JWT (access + refresh) and API keys for machine-to-machine access, with role-based access control

## Technology Stack

| Concern | Choice |
|---|---|
| Framework | FastAPI |
| Language | Python 3.12+ |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| AI | OpenAI-compatible API (Gemini by default) |

## Architecture

```
app/api/            → Routes (FastAPI routers) + Pydantic schemas
app/application/    → Services (business logic) + repository interfaces
app/domain/         → SQLAlchemy ORM models (entities)
app/infrastructure/ → Repository implementations + DB session
```

Dependency flow: `api → application → domain ← infrastructure`. Dependencies are wired in [app/api/deps.py](app/api/deps.py) and injected into route handlers via FastAPI's `Depends()`.

---

## Prerequisites

- Python **3.12+**
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- PostgreSQL (or Docker, which provides it)

## Getting Started

### 1. Clone and configure

```bash
git clone <your-repository-url>
cd FormForge_API
cp env.template .env
```

Open `.env` and set the database credentials, `GEMINI_API_KEY`, and a `SECRET_KEY`. The secret key is **required** — generate one with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Run with Docker (recommended)

Start the full stack (API + PostgreSQL + pgAdmin):

```bash
docker compose up -d --build
```

Or run only the database and pgAdmin, and develop the API locally:

```bash
./dev.sh
```

### 3. Run locally with uv

```bash
uv sync                    # install dependencies
uv run alembic upgrade head   # apply migrations
uv run dev                 # start the dev server (hot reload)
```

### Services & Ports

| Service | URL |
|---|---|
| API | http://localhost:8001 |
| Swagger docs | http://localhost:8001/docs |
| PostgreSQL | localhost:5432 |
| pgAdmin | http://localhost:5051 |

---

## Common Commands

```bash
# Server
uv run dev                                   # dev server with hot reload

# Migrations
uv run alembic upgrade head                  # apply all migrations
uv run alembic revision --autogenerate -m "message"   # generate a migration
uv run alembic downgrade -1                  # roll back one migration

# Database seeding
uv run seed                                  # seed test data
uv run seed --clear                          # clear and reseed
uv run reset-db                              # full reset (asks for confirmation)
```

Inside Docker, prefix with `docker compose exec api`, e.g.:

```bash
docker compose exec api uv run alembic upgrade head
```

---

## Authentication

- **JWT** (HS256): access token (30 min) + refresh token (7 days). Obtain tokens via `POST /api/auth/login` or `/api/auth/register`.
- **API keys** (M2M): create via `POST /api/auth/api-keys`, then send on requests using the `X-API-Key` header. Keys carry scopes (`read` / `write` / `delete`) and an optional expiry. Endpoints that accept keys take **either** a JWT or a key — the Bearer token wins when both are present, and scopes are enforced only for key-authenticated requests.

## Environment Variables

Copy `env.template` to `.env`. Key variables:

| Variable | Description |
|---|---|
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` | PostgreSQL connection |
| `DB_ECHO` | Log every SQL statement (default `false`; dev only) |
| `SECRET_KEY` | JWT signing key — **required, no default** |
| `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS` | JWT lifetimes |
| `GEMINI_API_KEY` | API key for the AI provider |
| `AI_BASE_URL`, `AI_MODEL` | AI provider endpoint and model (OpenAI-compatible; defaults to Gemini) |

---

## API Documentation

Interactive OpenAPI docs are available at **http://localhost:8001/docs** while the server is running.
