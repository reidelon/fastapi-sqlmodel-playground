import json
import os
from datetime import datetime

from fastapi import FastAPI, Depends
from google.cloud import pubsub_v1
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import init_db, get_session
from app.models import Song, SongCreate

publisher = pubsub_v1.PublisherClient()
TOPIC_PATH = publisher.topic_path(os.environ.get("GCP_PROJECT_ID", "fastapi-demo-2026"), "song-created")

app = FastAPI()

# commenting it out bc the schema is stable and the tables already exist in the DB
# @app.on_event("startup")
# async def on_startup():
#     await init_db()


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}


@app.get("/songs", response_model=list[Song])
async def get_songs(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Song))
    songs = result.scalars().all()
    return songs


@app.post("/songs", response_model=Song)
async def add_song(song: SongCreate, session: AsyncSession = Depends(get_session)):
    db_song = Song(name=song.name, artist=song.artist, year=song.year)
    session.add(db_song)
    await session.commit()
    await session.refresh(db_song)

    message = json.dumps({
        "event": "song_created",
        "song_id": db_song.id,
        "name": db_song.name,
        "artist": db_song.artist,
        "year": db_song.year,
        "timestamp": datetime.utcnow().isoformat(),
    }).encode("utf-8")
    publisher.publish(TOPIC_PATH, message)

    return db_song