# FastAPI + SQLModel Async API

Exploring async patterns with FastAPI, SQLModel, and SQLAlchemy's async engine.
The main goal was understanding how async I/O works end-to-end — from the ASGI server down to the database driver.

## Stack

- **FastAPI** — ASGI web framework
- **SQLModel** — models and schema (built on SQLAlchemy + Pydantic)
- **SQLAlchemy AsyncEngine** — async database engine (not SQLModel's default sync engine)
- **aiosqlite** — async SQLite driver
- **Uvicorn** — ASGI server
- **Alembic** — database migrations

## Why AsyncEngine directly?

SQLModel ships with a sync `create_engine` by default. Here I use SQLAlchemy's
`create_async_engine` + `AsyncSession` directly to get true non-blocking DB calls,
which matters when running under an async server like Uvicorn.

## Project structure

```
app/
  main.py    # FastAPI routes
  db.py      # Async engine and session setup
  models.py  # SQLModel table definitions
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database migrations.

Apply all migrations:

```bash
alembic upgrade head
```

Create a new migration after model changes:

```bash
alembic revision --autogenerate -m "description"
```

Check current state:

```bash
alembic current
alembic history
```

Roll back to a previous revision:

```bash
alembic downgrade <revision_id>
```

## Run

```bash
uvicorn app.main:app --reload
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ping` | Health check |
| GET | `/songs` | List all songs |
| POST | `/songs` | Add a song |
| GET | `/docs` | Swagger UI — interactive docs |
| GET | `/redoc` | ReDoc — alternative docs |

## Environment

By default uses a local SQLite database. Override with:

```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/dbname"
```