# FastAPI + SQLModel Async API

Async REST API built with FastAPI, SQLModel and SQLAlchemy's async engine, deployed on Google Cloud Platform.

The main goal was learning async patterns end-to-end — from the ASGI server down to the database driver — and integrating GCP services (Cloud Run, Pub/Sub, Cloud Storage).

## Live URL

```
https://awesome-project-647908985071.us-central1.run.app
```

- Health check: `GET /ping`
- Swagger UI: `GET /docs`

## Stack

- **FastAPI** — ASGI web framework
- **SQLModel** — models and schema (built on SQLAlchemy + Pydantic)
- **SQLAlchemy AsyncEngine** — async database engine (not SQLModel's default sync engine)
- **aiosqlite** — async SQLite driver
- **Uvicorn** — ASGI server
- **Alembic** — database migrations
- **Docker** — containerization
- **GCP Cloud Run** — serverless container hosting
- **GCP Cloud Pub/Sub** — async event messaging
- **GCP Cloud Storage** — file storage

## Architecture

```
POST /songs
    → saves to SQLite DB
    → publishes event to Pub/Sub topic (song-created)
        → push subscriber triggers Cloud Function (save-song-to-storage)
            → Cloud Function saves song JSON to Cloud Storage bucket
```

### GCP resources

| Resource | Name |
|---|---|
| GCP Project | `fastapi-demo-2026` |
| Cloud Run service | `awesome-project` (region: us-central1) |
| Pub/Sub topic | `song-created` |
| Pub/Sub pull subscriber | `song-created-sub` |
| Pub/Sub push subscriber | `song-to-storage-push` |
| Cloud Function | `save-song-to-storage` |
| Cloud Storage bucket | `fastapi-demo-2026-songs` |

## Why AsyncEngine directly?

SQLModel ships with a sync `create_engine` by default. Here I use SQLAlchemy's
`create_async_engine` + `AsyncSession` directly to get true non-blocking DB calls,
which matters when running under an async server like Uvicorn.

## Project structure

```
app/
  main.py    # FastAPI routes + Pub/Sub publisher
  db.py      # Async engine and session setup
  models.py  # SQLModel table definitions
cloud-functions/
  song-to-storage/
    main.py          # Cloud Function: Pub/Sub push subscriber → Cloud Storage
    requirements.txt
migrations/          # Alembic migrations
```

## Local setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Run with Docker

```bash
docker build -t awesome-project .
docker run -p 8080:8080 awesome-project
```

## Deploy to Cloud Run

```bash
gcloud run deploy awesome-project \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --project=fastapi-demo-2026
```

## Deploy Cloud Function

```bash
gcloud functions deploy save-song-to-storage \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=cloud-functions/song-to-storage \
  --entry-point=save_song_to_storage \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars BUCKET_NAME=fastapi-demo-2026-songs \
  --project=fastapi-demo-2026
```

## Migrations

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "description"

# Check current state
alembic current
alembic history

# Roll back
alembic downgrade <revision_id>
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ping` | Health check |
| GET | `/songs` | List all songs |
| POST | `/songs` | Add a song |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |

### Example

```bash
curl -X POST https://awesome-project-647908985071.us-central1.run.app/songs \
  -H "Content-Type: application/json" \
  -d '{"name": "Bohemian Rhapsody", "artist": "Queen", "year": 1975}'
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///database.db` | Database connection string |
| `GCP_PROJECT_ID` | `fastapi-demo-2026` | GCP project ID for Pub/Sub |

> Note: SQLite is ephemeral on Cloud Run — data does not persist across container restarts. Production would use Cloud SQL (PostgreSQL).

## Verify Pub/Sub messages (pull)

```bash
gcloud pubsub subscriptions pull song-created-sub \
  --project=fastapi-demo-2026 \
  --limit=10
```

## Verify Cloud Storage files

```bash
gcloud storage ls gs://fastapi-demo-2026-songs --project=fastapi-demo-2026
gcloud storage cat gs://fastapi-demo-2026-songs/<filename>.json --project=fastapi-demo-2026
```