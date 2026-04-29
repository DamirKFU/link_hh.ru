# Vlad FastAPI 2

Backend API service on FastAPI with PostgreSQL, Redis, Alembic migrations, cookie-based JWT authentication, and i18n tooling.

## Requirements

- Python 3.12+
- PostgreSQL
- Redis

## Installation

From repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuration

Environment file path: `backend/.env`.

Environment selection:

- `APP_ENV=dev` for development settings
- `APP_ENV=prod` for production settings (reads `backend/prod.env`)

Required variables:

- `APP__CORE__SECRET_KEY`
- `APP__DB__URL`
- `APP__GOOGLE__SECRET`
- `APP__GOOGLE__CLIENT_ID`
- `APP__MAIL__BACKEND` (`smtp` or `file`)

If `APP__MAIL__BACKEND=smtp`, also set:

- `APP__MAIL__USERNAME`
- `APP__MAIL__PASSWORD`
- `APP__MAIL__FROM_EMAIL`
- `APP__MAIL__SERVER`

## Run

From repository root:

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Alternative CLI entrypoint:

```bash
python -m backend run
```

## Migrations

Alembic commands are available through CLI:

```bash
python -m backend alembic revision -m "message"
python -m backend alembic upgrade head
python -m backend alembic downgrade -1
python -m backend alembic current -v
python -m backend alembic history -v
```

## i18n Commands

```bash
python -m backend i18n extract
python -m backend i18n init --lang en
python -m backend i18n update
python -m backend i18n compile
```

## API Routes

Base prefix: `/api`.

Implemented routes:

- `/api/auth/v1/register`
- `/api/auth/v1/login`
- `/api/auth/v1/logout`
- `/api/auth/v1/refresh`
- `/api/auth/v1/forgot-password`
- `/api/auth/v1/reset-password`
- `/api/auth/v1/send-verification`
- `/api/auth/v1/confirm-email`

## Project Structure

- `backend/main.py`: FastAPI app export
- `backend/core/registrar.py`: app initialization and middleware wiring
- `backend/cli.py`: CLI commands (`run`, `alembic`, `i18n`)
- `backend/apps/`: API routers and domain modules
- `backend/database/`: DB and Redis integrations
- `backend/common/`: shared auth, responses, logging, exceptions
- `backend/alembic/`: migration environment and versions
